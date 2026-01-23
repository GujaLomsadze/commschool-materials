from airflow import DAG
from airflow.providers.postgres.sensors.postgres import PostgresTableSensor
from airflow.operators.python import PythonOperator
from datetime import datetime


def do_something():
    print("✅ Data is available, continuing pipeline...")


with DAG(
        dag_id="example_postgres_table_sensor",
        start_date=datetime(2025, 1, 1),
        schedule="@hourly",
        catchup=False,
        tags=["sensor", "postgres"],
) as dag:
    wait_for_data = PostgresTableSensor(
        task_id="wait_for_data_in_table",
        postgres_conn_id="postgres_default",  # must exist in Airflow Connections
        table="public.orders",  # waits until table is NOT empty
        poke_interval=30,  # check every 30 seconds
        timeout=10 * 60,  # fail after 10 minutes
        mode="poke",  # most simple mode
    )

    process = PythonOperator(
        task_id="process_orders",
        python_callable=do_something,
    )

    wait_for_data >> process
