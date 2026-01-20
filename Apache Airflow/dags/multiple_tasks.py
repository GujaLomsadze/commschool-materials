from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


def extract():
    print("Extracting data...")


def transform():
    print("Transforming data...")


def load():
    print("Loading data...")


with DAG(
        dag_id="example_etl_pipeline",
        start_date=datetime(2025, 1, 1),
        schedule="@hourly",
        catchup=False,
) as dag:
    t1 = PythonOperator(task_id="extract", python_callable=extract)
    t2 = PythonOperator(task_id="transform", python_callable=transform)
    t3 = PythonOperator(task_id="load", python_callable=load)

    t1 >> t2 >> t3
