from datetime import datetime, timedelta
import os
import time
import requests

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.python import PythonOperator
from bungalow_operators.weather import WeatherAPIOperator, UploadRawCurrentWeatherOperator
from bungalow_operators.ops import DagRunOperator
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
DAG_ID = 'fetcher'

with DAG(
        DAG_ID,
        default_args=default_args,
        description='To fetch the bungalow_operators data',
        schedule_interval=timedelta(minutes=5),
        start_date=datetime(2021, 1, 1),
        catchup=False,
        tags=['take-home'],
) as dag:
    t1 = DagRunOperator.start(
        task_id='ops_dag_run_init',
        name='ops_init_run',
        _dag_id=DAG_ID
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

    t4 = DagRunOperator.update_status(
        task_id='ops_dag_run_success',
        name='ops_update_status',
        status='SUCCESS',
        _dag_id=DAG_ID
    )

    t1 >> t2 >> t3 >> t4
