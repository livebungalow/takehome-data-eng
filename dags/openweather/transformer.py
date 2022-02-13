from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'retries': 0,
    'retry_delay': timedelta(minutes=1)
}

with DAG(
    'transformer',
    default_args=default_args,
    description='To transform the raw current weather to a modeled dataset',
    start_date=datetime(2021, 1, 1, 0, 0, 0),
    schedule_interval="5 */2 * * *",
    catchup=False,
    tags=['take-home'],
) as dag:

    create_modeled_dataset_table = PostgresOperator(
        task_id="create_modeled_dataset_table",
        sql="sql/create_current_weather_tbl.sql",
    )

    transform_raw_into_modelled = PostgresOperator(
        task_id="transform_raw_into_modelled",
        sql="sql/transform_raw_weather_to_current_weather.sql",
    )

    create_modeled_dataset_table >> transform_raw_into_modelled

