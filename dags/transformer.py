from datetime import datetime, timedelta

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.providers.postgres.operators.postgres import PostgresOperator
from bungalow_operators.ops import TransformerDagRunOperator
from bungalow_operators.weather import RawToStageCityOperator, RawToStageWeatherOperator
from fetcher import FETCHER_DAG_ID

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}
DAG_ID = 'transformer'

with DAG(
        DAG_ID,
        default_args=default_args,
        description='To transform the raw current bungalow_operators to a modeled dataset',
        schedule_interval=timedelta(minutes=5),
        start_date=datetime(2021, 1, 1),
        catchup=False,
        tags=['take-home'],
        params={'fetcher_run_id': None},
) as dag:

    t1 = TransformerDagRunOperator.start(
        task_id='ops_dag_transformer_run_init',
        name='ops_transformer_run',
        _dag_id=DAG_ID,
        fetcher_dag_id=FETCHER_DAG_ID
    )

    t2a = RawToStageWeatherOperator(
        task_id="raw_to_stage_weather",
        name='transform_t1_to_stage_weather',
        _dag_id=DAG_ID
    )
    t2b = RawToStageCityOperator(
        task_id="raw_to_stage_city",
        name='transform_t1_to_stage_city',
        _dag_id=DAG_ID
    )
    t1 >> t2b >> t2a
    # t1 >> [t2a, t2b], t3 >> t4 >> t5]
    # t3: validation
    # t4: upsert
    # t5: ops update status
