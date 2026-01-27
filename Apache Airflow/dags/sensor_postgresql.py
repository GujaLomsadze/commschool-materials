from airflow import DAG
from airflow.providers.common.sql.sensors.sql import SqlSensor
from airflow.operators.python import PythonOperator
from datetime import datetime


def do_something():
    print("✅ Data is available, continuing pipeline...")


def do_something2():

    print("✅ Data is available, continuing pipeline...")


with DAG(
        dag_id="example_postgres_table_sqlsensor",
        start_date=datetime(2025, 1, 1),
        schedule="@hourly",
        catchup=False,
        tags=["sensor", "postgres", "sqlsensor"],
) as dag:


    start = PythonOperator(
        task_id="process_orders2",
        python_callable=do_something2,
    )

    wait_for_data = SqlSensor(
        task_id="wait_for_data_in_table",
        conn_id="postgres_default",  # Airflow Connection ID
        sql="SELECT 1 FROM public.variable LIMIT 1;",
        poke_interval=5,
        timeout=10 * 60,
        mode="poke",  # or "reschedule" (recommended for long waits)
    )

    process = PythonOperator(
        task_id="process_orders",
        python_callable=do_something,
    )

    start >> wait_for_data >> process
