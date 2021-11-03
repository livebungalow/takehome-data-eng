from datetime import datetime, timedelta
from textwrap import dedent

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
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
with DAG(
        'fetcher',
        default_args=default_args,
        description='To fetch the weather data',
        schedule_interval=timedelta(minutes=5),
        start_date=datetime(2021, 1, 1),
        catchup=False,
        tags=['take-home'],
) as dag:

    # @TODO: Remove or replace with Python Operator. Hint: How to fetch the weather data from https://www.aerisweather.com/?
    t1 = BashOperator(
        task_id='print_date',
        bash_command='date',
    )

    # @TODO: Fill in the below
    t2 = PostgresOperator(
        task_id="Create raw data table",
        sql="""
            CREATE TABLE IF NOT EXISTS raw_current_weather (
           );
          """,
    )

    # @TODO: Fill in the below
    t3 = PostgresOperator(
        task_id="store the data in the table",
        sql="""
            INSERT INTO ...
          """,
    )

    t1 >> t2 >> t3