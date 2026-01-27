from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import logging

logger = logging.getLogger("airflow.task")


def start_task():
    logger.info("Start task 🚦")


def process_item(item):
    logger.info(f"Processing item: {item}")


def end_task():
    logger.info("End task 🏁")


items = ["A", "B", "C", "D", "E", "F", "G"]

with DAG(
        dag_id="dynamic_set_downstream_dag",
        start_date=datetime(2024, 1, 1),
        schedule_interval="@daily",
        catchup=False,
        tags=["dynamic", "set_downstream"],
) as dag:
    start = PythonOperator(
        task_id="start",
        python_callable=start_task,
    )

    end = PythonOperator(
        task_id="end",
        python_callable=end_task,
    )

    for item in items:
        task = PythonOperator(
            task_id=f"process_{item}",
            python_callable=process_item,
            op_args=[item],
        )
        # Explicit dependency wiring
        start.set_downstream(task)
        task.set_downstream(end)
