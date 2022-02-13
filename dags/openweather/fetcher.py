import json
import typing
import logging

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_f0ilure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'fetcher',
    default_args=default_args,
    description='To fetch the weather data',
    start_date=datetime(2021, 1, 1, 0, 0, 0),
    schedule_interval="0 */2 * * *",
    catchup=False,
    tags=['take-home'],
) as dag:

    create_raw_dataset = PostgresOperator(
        task_id="create_raw_dataset",
        sql="sql/create_raw_current_weather_tbl.sql",
    )

    def run_extract(api_key: str, city_ids: typing.List[str], save_to_file: bool = False) -> typing.List[typing.Tuple]:
        """
        Pull payload from OpenWeatherAPI from a list of city IDs.
        """
        from openweather.op.extract import OpenWeatherMapExtractor

        extractor = OpenWeatherMapExtractor(api_key=api_key)
        rows = []
        for city_id in city_ids:
            payload = extractor.get_current_weather(city_id=city_id)
            if payload:
                # At this stage (didn't implement) we could implement
                # some kind of schema validation (pydantic, etc.)
                # to enforce what we expect to be defined from the payload.
                rows.append((
                    payload['id'],
                    payload['dt'],
                    payload['timezone'],
                    json.dumps(payload),
                ))
            # This is POC to show one route we could take.
            if save_to_file:
                # Would use a better logging message here.
                logging.info("Writing to file...")
                # In practice we'd write to S3 or something
                with open("./dump_file.json", "a") as persist_to:
                    persist_to.write(json.dumps(payload))
        return rows

    ingest_api_data = PythonOperator(
        task_id='ingest_api_data',
        python_callable=run_extract,
        # We can tweak if we want to retry this many times
        retries=3,
        op_kwargs={
            # In practice, for security, grab it from env var
            # or pass it via UI config
            'api_key' : 'a6e6e5ef01421b25be04a1a6efbd7ead',
            # KW, London (ON)
            'city_ids' : ['5992996', '6058560'],
        },
    )

    def construct_insert_statement(**context) -> str:
        """
        Using result from run_extract/t2, construct INSERT INTO ... VALUES statement string.
        """
        rows = context['ti'].xcom_pull(
            key='return_value',
            task_ids='ingest_api_data',
        )
        value_rows = [
            "({}, {}, {}, '{}', {}, {})".format(
                row[0],
                row[1],
                row[2],
                row[3],
                "now()",
                "now()"
            )
            for row in rows
        ]
        values_stmt = ',\n'.join(value_rows)

        from textwrap import dedent

        # Could also do this in a separate file.
        return dedent(f"""
        SET TIME ZONE 'UTC';

        INSERT INTO raw_current_weather (city_id, unix_time_seconds, tz_offset_seconds, raw_data, created_at, updated_at)
            VALUES
                {values_stmt}

        ON CONFLICT (city_id, unix_time_seconds) DO
            UPDATE SET
                tz_offset_seconds = EXCLUDED.tz_offset_seconds,
                raw_data = EXCLUDED.raw_data,
                updated_at = EXCLUDED.updated_at
        """)


    # We could've also shoved t3 and t2 into one task, but I like the separation.
    construct_insert_statement = PythonOperator(
        task_id='construct_insert_statement',
        python_callable=construct_insert_statement,
        provide_context=True,
    )

    insert_into_raw_dataset = PostgresOperator(
        task_id='insert_into_raw_dataset',
        sql="{{ ti.xcom_pull(key='return_value', task_ids='construct_insert_statement') }}",
    )

    create_raw_dataset >> ingest_api_data >> construct_insert_statement >> insert_into_raw_dataset

