from airflow import DAG
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.operators.python import PythonOperator 
from airflow.utils.dates import days_ago
from datetime import datetime

import requests
import json

LATITUDE = "51.50740"
LONGITUDE = "-0.1278"

MYSQL_CONN_ID = "mysql_weather_api"
API_CONN_ID = "open_meteo_api"


def extract_weather_data(ti,**kwargs):
    
    print("<<<<<<<<<<<<<<<<<<<<<< Extracting weather data >>>>>>>>>>>>>>>>>>>>>>");

    # Use http hook to get the connection details from Airflow connection
    hook = HttpHook(method='GET', http_conn_id=API_CONN_ID)
    
    # Full endpoint path after the base URL
    endpoint = f"/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true"
    
    response = hook.run(endpoint)
    data = response.json()

    if response.status_code == 200:
        data = response.json()

        print("Raw weather data from api *********** :", data)

        print("Total entries in the db : ",len(data))

        ti.xcom_push(key='raw_weather_data', value=data)

    else:
        raise Exception(f"Failed to fetch weather data: {response.status_code}")

def transform_weather_data(ti,**kwargs):

    weather_data = ti.xcom_pull(task_ids='extract_weather_data', key='raw_weather_data')

    # Transform the extracted weather data
    current_weather = weather_data["current_weather"];

    transformed_data = {
        'latitude':LATITUDE,
        'longitude':LONGITUDE,
        "temperature":current_weather["temperature"],
        "windspeed":current_weather["windspeed"],
        "winddirection":current_weather["winddirection"],
        "weathercode":current_weather["weathercode"]
    }

    print("Transformed data : ",transformed_data)

    ti.xcom_push(key='transformed_weather_data', value=transformed_data)


def load_weather_data(ti,**kwargs):
    
    transformed_data = ti.xcom_pull(task_ids='transform_weather_data', key='transformed_weather_data')


    """Load transformed data into PostgreSQL."""

    mysql_hook = MySqlHook(mysql_conn_id=MYSQL_CONN_ID)
    conn = mysql_hook.get_conn()
    cursor = conn.cursor()


        # Create table if it doesn't exist
    cursor.execute("""
                            CREATE TABLE IF NOT EXISTS weather_data (
                                latitude FLOAT,
                                longitude FLOAT,
                                temperature FLOAT,
                                windspeed FLOAT,
                                winddirection FLOAT,
                                weathercode INT,
                                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            );
                    """)

    # Insert transformed data into the table
    cursor.execute(""" INSERT INTO weather_data (latitude, longitude, temperature, windspeed, winddirection, weathercode)
                           VALUES (%s, %s, %s, %s, %s, %s)
                            """, (
            transformed_data['latitude'],
            transformed_data['longitude'],
            transformed_data['temperature'],
            transformed_data['windspeed'],
            transformed_data['winddirection'],
            transformed_data['weathercode']
        ))

    conn.commit()
    cursor.close()


default_args = {
    "owner":"airflow",
    "start_date":days_ago(1)
}

dag = DAG( dag_id='weather_etl_pipeline', default_args= default_args, schedule_interval='4 0 * * *',catchup=False)


extract_task = PythonOperator(
    task_id='extract_weather_data',
    python_callable=extract_weather_data,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform_weather_data',
    python_callable=transform_weather_data,
    dag=dag
)

load_task = PythonOperator(
    task_id='load_weather_data',
    python_callable=load_weather_data,
    dag=dag
)

extract_task >> transform_task >> load_task