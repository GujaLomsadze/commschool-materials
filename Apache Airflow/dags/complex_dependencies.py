from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


# ---- Empty / demo functions ----
def start():
    pass


def extract_a():
    pass


def extract_b():
    pass


def transform_a():
    pass


def transform_b():
    pass


def validate():
    pass


def load():
    pass


def notify_success():
    pass


def notify_failure():
    pass


with DAG(
        dag_id="example_complex_dependencies_trigger_rules",
        start_date=datetime(2025, 1, 1),
        schedule=None,
        catchup=False,
) as dag:
    # ---- Tasks ----
    t_start = PythonOperator(task_id="start", python_callable=start)

    t_extract_a = PythonOperator(task_id="extract_a", python_callable=extract_a)
    t_extract_b = PythonOperator(task_id="extract_b", python_callable=extract_b)

    t_transform_a = PythonOperator(task_id="transform_a", python_callable=transform_a)
    t_transform_b = PythonOperator(task_id="transform_b", python_callable=transform_b)

    # Join task: runs as long as *at least one* upstream task succeeded
    t_validate = PythonOperator(
        task_id="validate",
        python_callable=validate,
        trigger_rule="none_failed_min_one_success",
    )

    # Load should run only if validation succeeded
    t_load = PythonOperator(
        task_id="load",
        python_callable=load,
        trigger_rule="all_success",
    )

    # Notification tasks:
    t_notify_success = PythonOperator(
        task_id="notify_success",
        python_callable=notify_success,
        trigger_rule="all_success",  # only if everything before succeeded
    )

    # t_notify_failure = PythonOperator(
    #     task_id="notify_failure",
    #     python_callable=notify_failure,
    #     trigger_rule="one_failed",  # runs if ANY upstream failed
    # )

    # ---- Dependencies (complex graph) ----
    t_start >> [t_extract_a, t_extract_b]

    t_extract_a >> t_transform_a
    t_extract_b >> t_transform_b

    # join both transform paths into validate
    [t_transform_a, t_transform_b] >> t_validate

    # validation must happen before load
    t_validate >> t_load

    # success notification if whole pipeline succeeded
    t_load >> t_notify_success
    #
    # # failure notification watches everything upstream (common real-world pattern)
    # [
    #     t_extract_a,
    #     t_extract_b,
    #     t_transform_a,
    #     t_transform_b,
    #     t_validate,
    #     t_load,
    # ] >> t_notify_failure
