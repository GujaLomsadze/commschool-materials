from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime


def extract():
    x = 1/0
    print("Extracting data...")


def transform():
    x = 1 / 0
    print("Transforming data...")


def load():
    x  = 1/0
    print("Loading data...")


def notify():
    print("Notifying data...")


with DAG(
        dag_id="example_etl_pipeline",
        start_date=datetime(2025, 1, 1),
        schedule="@hourly",
        catchup=False,
) as dag:
    t1 = PythonOperator(task_id="extract", python_callable=extract)
    t2 = PythonOperator(task_id="transform", python_callable=transform, trigger_rule=TriggerRule.ONE_DONE)
    t3 = PythonOperator(task_id="load", python_callable=load, trigger_rule=TriggerRule.ONE_DONE)
    notify_failed = PythonOperator(task_id="notify_failed",
                                   python_callable=notify,
                                   trigger_rule=TriggerRule.ALL_FAILED
                                   )

    t1 >> t2 >> t3
    t1 >> notify_failed
    t2 >> notify_failed
    t3 >> notify_failed
