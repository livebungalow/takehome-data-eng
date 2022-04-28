from datetime import datetime, timedelta
import time

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

from scripts.process_weather_data import main
import os

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}
with DAG(
    "fetcher",
    default_args=default_args,
    description="To fetch the weather data",
    schedule_interval=timedelta(minutes=5),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["take-home"],
) as dag:

    # @TODO: Fill in the below
    t1 = PostgresOperator(
        task_id="create_raw_dataset",
        sql="sql/create_raw_current_weather.sql",
    )

    t2 = PythonOperator(
        task_id="ingest_api_data",
        python_callable=print_env_var,
        # op_kwargs={'random_base': 101.0 / 10},
    )

    t1 >> t2
