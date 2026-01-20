from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


def generate_number():
    number = 42
    print(f"Generated number: {number}")
    return number  # returned value is stored in XCom automatically


def use_number(ti):
    number = ti.xcom_pull(task_ids="generate_number")
    print(f"Pulled from XCom: {number}")
    print(f"Number * 2 = {number * 2}")


with DAG(
        dag_id="example_xcom",
        start_date=datetime(2025, 1, 1),
        schedule=None,  # manual trigger
        catchup=False,
) as dag:
    gen = PythonOperator(
        task_id="generate_number",
        python_callable=generate_number,
    )

    use = PythonOperator(
        task_id="use_number",
        python_callable=use_number,
    )

    gen >> use
