from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import logging

logger = logging.getLogger("airflow.task")


def process_step(step):
    logger.info(f"Running step {step}")


steps = [1, 2, 3, 4]

with DAG(
        dag_id="dynamic_sequential_dag",
        start_date=datetime(2024, 1, 1),
        schedule_interval="@daily",
        catchup=False,
        tags=["dynamic", "sequential"],
) as dag:
    previous_task = None

    for step in steps:
        current_task = PythonOperator(
            task_id=f"step_{step}",
            python_callable=process_step,
            op_args=[step],
        )

        if previous_task:
            previous_task.set_downstream(current_task)

        previous_task = current_task
