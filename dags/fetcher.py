from datetime import datetime, timedelta
import os
import time
import requests

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.python import PythonOperator
from bungalow_operators.weather import WeatherAPIOperator, UploadRawCurrentWeatherOperator
from bungalow_operators.ops import FetcherDagRunOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

DEFAULT_CITIES = ['Vancouver', 'Toronto', 'Montreal']
FETCHER_DAG_ID = 'fetcher'

with DAG(
        FETCHER_DAG_ID,
        default_args=default_args,
        description='To fetch the bungalow_operators data',
        schedule_interval=timedelta(minutes=5),
        start_date=datetime(2021, 1, 1),
        catchup=False,
        tags=['take-home'],
) as dag:
    t1 = FetcherDagRunOperator.start(
        task_id='ops_dag_fetcher_run_init',  # Should live as a constant
        name='ops_fetcher_run',
        _dag_id=FETCHER_DAG_ID
    )

    t2 = WeatherAPIOperator.from_cities(
        task_id='ingest_api_data',
        name='get_weather_data',
        cities=DEFAULT_CITIES
    )

    t3 = UploadRawCurrentWeatherOperator(
        task_id='upload_raw_data',
        name='upload_raw_weather_data',
    )

    # Improvement, this should be conditional on how the tasks went
    t4 = FetcherDagRunOperator.update_status(
        task_id='ops_dag_fetcher_success',
        name='ops_fetcher_update_status',
        status='SUCCESS',
        start_task_id='ops_dag_fetcher_run_init',
        _dag_id=FETCHER_DAG_ID
    )

    t1 >> t2 >> t3 >> t4
