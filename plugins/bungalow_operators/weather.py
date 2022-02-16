import json
import os
import logging
import requests
from datetime import datetime
from typing import List, Tuple, Any
from airflow.models.baseoperator import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from bungalow_operators import DEFAULT_POSTGRES_CONN_ID

logger = logging.getLogger('bungalow_operators')
logger.setLevel(logging.INFO)


class WeatherAPIOperator(BaseOperator):
    api_key = os.environ.get('OPEN_WEATHER_API_KEY')
    base_url = 'http://api.openweathermap.org/data/2.5/weather'
    template_fields = ['name', 'list_query_parameters']

    def __init__(self, name: str, list_query_parameters: List[str], **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = name
        self.list_query_parameters = list_query_parameters
        self.data = {}

    def __repr__(self):
        return self.name

    @classmethod
    def from_cities(cls, name: str, cities: List[str], **kwargs):
        # Codes must follow ISO-3166 convention
        return cls(name=name, list_query_parameters=cities, **kwargs)

    @classmethod
    def from_coords(cls, name, coords: List[Tuple], **kwargs):
        list_query_parameters = [f'lat={lat}&lon={lon}' for lat, lon in coords]
        return cls(name, query_parameters=list_query_parameters, **kwargs)

    def get_url(self, query_parameters):
        return '{base_url}?q={query_parameters}&appid={api_key}'.format(base_url=self.base_url,
                                                                        query_parameters=query_parameters,
                                                                        api_key=self.api_key)

    def execute(self, context: Any):
        for query_parameters in self.list_query_parameters:
            logger.info('[+] %s', query_parameters)

            url = self.get_url(query_parameters=query_parameters)
            r = requests.get(url)
            logger.info('[+] Status Code %s', str(r.status_code))

            r.raise_for_status()  # Raise exception if necessary
            self.data[query_parameters] = r.json()
            # Typically, this would be saved as a file, pushed to a place like s3
            # Since the dataset each run is small, keeping it as an xcom
        ti = context['task_instance']
        ti.xcom_push(key='data', value=self.data)


class UploadRawCurrentWeatherOperator(BaseOperator):
    template_fields = ['name']

    target = 'raw_current_weather'
    columns = ['run_id', 'ran_at', 'calculated_at', 'location', 'city_id', 'data']
    columns_str = ', '.join(columns)
    base_values = '(%s, %s, %s, %s, %s, %s)'
    base_sql = 'INSERT INTO {target} ({columns_str}) VALUES {values};'

    def __init__(self, name: str, _dag_id: str = None, conn_id: str = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = name
        self.hook = PostgresHook(postgres_conn_id=conn_id or DEFAULT_POSTGRES_CONN_ID)

    def execute(self, context: Any):
        ti = context['task_instance']
        run_id = ti.xcom_pull(task_ids='ops_dag_fetcher_run_init', key='run_id')
        pulled_data = ti.xcom_pull(task_ids='ingest_api_data', key='data')

        rows = 0
        parameters = []
        for location, data in pulled_data.items():
            ran_at = datetime.now()

            location_parameters = [
                run_id, str(ran_at), str(datetime.fromtimestamp(data['dt'])),
                location, data['id'], json.dumps(data)
            ]
            parameters += location_parameters
            rows += 1

        query = self.base_sql.format(target=self.target, columns_str=self.columns_str,
                                     values=',\n'.join([self.base_values] * rows))
        self.hook.run(query, parameters=parameters)
