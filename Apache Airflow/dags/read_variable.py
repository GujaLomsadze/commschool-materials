from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime


def print_variable():
    # Reads an Airflow Variable (Admin -> Variables)
    x = Variable.get("x", default_var=0)
    print(f"x Variable = {x}")


with DAG(
        dag_id="read_variable",
        start_date=datetime(2025, 1, 1),
        schedule=None,
        catchup=False,
) as dag:
    t1 = PythonOperator(
        task_id="print_variable",
        python_callable=print_variable,
    )

    t1
