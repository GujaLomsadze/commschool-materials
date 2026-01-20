from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta


def extract(**context):
    print("Extracting data...")
    print(f"Run ID: {context['run_id']}")
    print(f"Execution date: {context['ds']}")


def transform(**context):
    print("Transforming data...")
    print(f"Task instance: {context['ti'].task_id}")


def load():
    print("Loading data...")
    print("Done.")


default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=10)
}

with DAG(
        dag_id="example_etl_pipeline_extra",
        description="Simple ETL DAG example for students (PythonOperator)",
        start_date=datetime(2025, 1, 1),
        schedule="@hourly",
        catchup=False,
        default_args=default_args,
        tags=["students", "etl", "pythonoperator"],
        max_active_runs=1,  # avoids overlapping DAG runs
) as dag:
    t1 = PythonOperator(
        task_id="extract",
        python_callable=extract,
        provide_context=True,  # older style; still common to see
        execution_timeout=timedelta(minutes=10),  # prevent endless tasks
        retries=3,  # override DAG default for this task
        retry_delay=timedelta(minutes=2),
    )

    t2 = PythonOperator(
        task_id="transform",
        python_callable=transform,
        provide_context=True,
        execution_timeout=timedelta(minutes=15),
    )

    t3 = PythonOperator(
        task_id="load",
        python_callable=load,
        provide_context=True,
        execution_timeout=timedelta(minutes=10),
    )

    t1 >> t2 >> t3
