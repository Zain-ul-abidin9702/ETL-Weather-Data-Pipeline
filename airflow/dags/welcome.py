from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from datetime import datetime
from airflow.utils.dates import days_ago  # recommended import
import requests



def print_welcome():
    print('Welcome to Airflow!')


def print_date():
    print('Today is and this is the new one {}'.format(datetime.today().date()))


def print_random_quote():

    # response = requests.get('<replace valid url here>')

    # quote = response.json()['content']

    name  = "zain";
    print("Print random quote",name);

def print_date_format():

    print("Printing the date format");

    print("TODAY DATE IS THIS ....");

    print("datetime.now : ",datetime.now());

    print("time delta : ",timedelta(days=1))
    
    print(f"{datetime.now() - timedelta(days=1)}")





dag = DAG(
    'welcome_dag',
    default_args={
        'start_date':days_ago(1)
    },
    schedule='4 0 * * *',
    catchup=False
)



print_welcome_task = PythonOperator(
    task_id='print_welcome',
    python_callable=print_welcome,
    dag=dag
)



print_date_task = PythonOperator(
    task_id='print_date',
    python_callable=print_date,
    dag=dag
)



print_random_quote = PythonOperator(
    task_id='print_random_quote',
    python_callable=print_random_quote,
    dag=dag
)

print_date_format = PythonOperator(
    task_id="print_date_format",
    python_callable=print_date_format,
    dag=dag
)
# Set the dependencies between the tasks

print_welcome_task >> print_date_task >> print_random_quote >> print_date_format