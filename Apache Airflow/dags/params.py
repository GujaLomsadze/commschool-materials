from airflow import DAG
from airflow.models.param import Param
from airflow.operators.python import PythonOperator
from datetime import datetime


def run_job(**context):
    p = context["params"]

    repeat = p["repeat"]
    debug = p["debug"]
    is_manual = p["is_manual"]
    threshold = p["threshold"]

    print(is_manual)


with DAG(
        dag_id="example_params_with_validation",
        start_date=datetime(2025, 1, 1),
        schedule="* * * * *",
        catchup=False,
        tags=["teaching", "params", "validation"],

        # ✅ strongly-typed + validated parameters
        params={
            "run_date": Param(
                default="2026-01-01",
                type="string",
                format="date",  # ✅ triggers calendar/date input in UI (when supported)
                description="Choose a date for the run",
            ),
            "name": Param(
                default="Student",
                type="string",
                minLength=1,
                description="Who should we greet?",
            ),
            "repeat": Param(
                default=3,
                type="integer",
                minimum=1,
                maximum=10,
                description="How many times to print the greeting",
            ),
            "debug": Param(
                default=False,
                type="boolean",
                description="If true, print extra debug details",
            ),
            "is_manual": Param(
                default=False,
                type="boolean",
                description="",
            ),
            "threshold": Param(
                default=0.8,
                type="number",
                minimum=0,
                maximum=1,
                description="A demo numeric parameter (0..1)",
            ),
        },
) as dag:
    task = PythonOperator(
        task_id="run_job",
        python_callable=run_job,
    )

    task
