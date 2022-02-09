from datetime import datetime, timedelta
import time
import requests

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from aiwsl ubunturflow.operators.python import PythonOperator
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
    response = dict()
    columns = (
                'lat', 'lon', 'weather_id', 'weather_main', 'weather_description', 'weather_icon','base', 'main_temp', 
                'main_feel_like', 'main_temp_max', 'main_temp_min', 'main_pressure', 'main_humidity', 'visibility', 
                'wind_speed', 'wind_deg', 'wind_gust', 'clouds_all', 'dt', 'sys_type', 'sys_id', 'sys_country', 
                'sys_sunrise', 'sys_sunset', 'timezone', 'name', 'id', 'cod'
    )
    values = ()

    # @TODO: Add your function here. Example here: https://airflow.apache.org/docs/apache-airflow/stable/_modules/airflow/example_dags/example_python_operator.html
    # Hint: How to fetch the weather data from OpenWeatherMap?
    def my_sleeping_function(random_base):
        """This is a function that will run within the DAG execution"""
        time.sleep(random_base)
        url = "http://api.openweathermap.org/data/2.5/weather?lat=35&lon=139&appid="
        api_key = "07349c660844361dd5bff04302472bd7"
        response = dict(requests.get(url+api_key).json())
        values = (response['coord']['lat'], response['coord']['lon'], response['weather']['id'], response['weather']['main'], response['weather']['description'],
                 response['weather']['icon'], response['base'], response['main']['temp'], response['main']['feels_like'], response['main']['temp_min'], response['main']['temp_max'], 
                 response['main']['pressure'], response['main']['humidity'], response['visibility'], response['wind']['speed'], response['wind']['deg'], response['wind']['gust'],
                 response['clouds']['all'], response['dt'], response['sys']['type'], response['sys']['id'], response['sys']['country'], response['sys']['sunrise'], response['sys']['sunset'],
                 response['timezone'], response['id'], response['name'], response['cod'])
        return response

    t1 = PythonOperator(
        task_id='ingest_api_data',
        python_callable=my_sleeping_function,
        op_kwargs={'random_base': 101.0 / 10},
    )

    # @TODO: Fill in the below
    t2 = PostgresOperator(
        task_id="create_raw_dataset",
        sql="""
            CREATE TABLE IF NOT EXISTS raw_current_weather (
                lat FLOAT,
                lon FLOAT,
                weather_id INT,
                weather_main VARCHAR,
                weather_description VARCHAR,
                weather_icon VARCHAR,
                base VARCHAR,
                main_temp FLOAT,
                main_feel_like FLOAT,
                main_temp_max FLOAT,
                main_temp_min FLOAT,
                main_pressure FLOAT,
                main_humidity FLOAT,
                visibility INT,
                wind_speed FLOAT,
                wind_deg INT,
                wind_gust FLOAT,
                clouds_all INT,
                dt BIGINT,
                sys_type INT,
                sys_id INT,
                sys_country VARCHAR,
                sys_sunrise BIGINT,
                sys_sunset BIGINT,
                timezone INT,
                name VARCHAR,
                id INT,
                cod INT,
                PRIMARY KEY (id)
           );
          """,

    # @TODO: Fill in the below
    t3 = PostgresOperator(
        task_id="store_dataset",
        sql=f'INSERT INTO raw_current_weather {columns} VALUES {values}',
    )

    t1 >> t2 >> t3