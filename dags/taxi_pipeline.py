from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
PROJECT = "/Users/akarshahegde/Documents/projects/nyc-taxi-pipeline"
with DAG (
dag_id="nyc-taxi-pipeline",
start_date=datetime(2026,11,1),
schedule="0 6 * * *",
catchup=False,) as dag:
    ingest=BashOperator(
    task_id="ingest",
    bash_command=f"cd {PROJECT} &&.venv/bin/python src/ingest.py",)
    load=BashOperator(
    task_id="load",
    bash_command=f"cd {PROJECT} &&.venv/bin/python src/load.py",)
    dbt_run=BashOperator(
    task_id="dbt_run",
    bash_command=f"cd {PROJECT}/taxi_dbt && ../.venv/bin/dbt run --profiles-dir .",)
    dbt_test = BashOperator(
    task_id="dbt_test",
    bash_command=f"cd {PROJECT}/taxi_dbt && ../.venv/bin/dbt test --profiles-dir .",)





    ingest >> load >> dbt_run >> dbt_test
