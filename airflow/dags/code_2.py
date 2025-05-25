from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.mysql_hook import MySqlHook
from datetime import datetime

def query_mysql():
    hook = MySqlHook(mysql_conn_id='my_mysql_conn')
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM learner LIMIT 5")
    results = cursor.fetchall()

    print("Results : ",results);
    for row in results:
        print(f"{row}====> ",row)

with DAG(
    dag_id='mysql_query_dag',
    start_date=datetime(2025, 5, 24),
    schedule_interval=None,
    catchup=False,
) as dag:
    query_task = PythonOperator(
        task_id='query_mysql_data',
        python_callable=query_mysql
    )
