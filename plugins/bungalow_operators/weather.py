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

        row_count = 0
        parameters = []
        for location, data in pulled_data.items():
            ran_at = datetime.now()

            location_parameters = [
                run_id, str(ran_at), str(datetime.fromtimestamp(data['dt'])),
                location, data['id'], json.dumps(data)
            ]
            parameters += location_parameters
            row_count += 1

        query = self.base_sql.format(target=self.target, columns_str=self.columns_str,
                                     values=',\n'.join([self.base_values] * row_count))
        self.hook.run(query, parameters=parameters)


class RawToStageOperator(BaseOperator):
    primary_key_name = None
    target = None

    columns = []
    base_sql = '''
        INSERT INTO {target} ({columns_str})
        VALUES
        {values}
        on conflict({conflict})
        {action}
        ;
    '''

    def __init__(self, name: str, _dag_id: str = None, conn_id: str = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self._dag_id = _dag_id
        self.hook = PostgresHook(postgres_conn_id=conn_id or DEFAULT_POSTGRES_CONN_ID)

    def query_raw_data(self, run_id) -> Tuple[str, List[str]]:
        raise NotImplementedError('[X] Must use child classes')

    def validate_row(self, row) -> None:
        # Write validations here, raising an exception if there is an error
        pass

    def query_upsert(self, row_count) -> str:
        query = self.base_sql.format(target=self.target, columns_str=self.columns_str,
                                     values=',\n'.join([self.base_values] * row_count),
                                     conflict=self.primary_key_name,
                                     action='do nothing')
        return query

    @property
    def columns_str(self):
        return ', '.join(self.columns)

    @property
    def base_values(self):
        return '({})'.format(', '.join(['%s'] * len(self.columns)))

    def execute(self, context: Any):
        ti = context['task_instance']
        # Should not be hard coded
        fetcher_run_id = ti.xcom_pull(task_ids='ops_dag_transformer_run_init', key='fetcher_run_id')
        logger.info('[+] fetcher_run_id: %s', fetcher_run_id)
        delta_query, delta_params = self.query_raw_data(run_id=fetcher_run_id)

        cur = self.hook.get_conn().cursor()
        cur.execute(delta_query, delta_params)

        row_count = 0
        values_to_upsert = []
        for row in cur:
            try:
                self.validate_row(row)
                values_to_upsert += row
                row_count += 1
            except Exception as e:
                # Future: Would be nice to be able to specify how to handle error
                logger.error('[X] Error resolving for %s = %s. Skipping', self.primary_key_name,
                             row[0])
                logger.error(e)
        upsert_query = self.query_upsert(row_count)
        self.hook.run(upsert_query, parameters=values_to_upsert)


class RawToStageCityOperator(RawToStageOperator):
    primary_key_name = 'city_id'
    target = 't2_cities'

    columns = ['lake_id', 'city_id', 'country', 'timezone', 'lat', 'lon']

    def query_raw_data(self, run_id) -> Tuple[str, List[str]]:
        base_sql = '''
        SELECT
        lake_id
        , city_id
        , data -> 'sys' ->> 'country'     as country
        , data ->> 'timezone'           as timezone
        , data -> 'coord' ->> 'lat'     as lat
        , data -> 'coord' ->> 'lon'     as lon
        FROM raw_current_weather
        WHERE run_id = %s
        '''
        return base_sql, [run_id]


class RawToStageWeatherOperator(RawToStageOperator):
    primary_key_name = 'sys_id'
    target = 't2_weather'

    columns = ['lake_id', 'sys_id', 'city_id', 'description', 'temp', 'humidity', 'pressure',
               'temp_max', 'temp_min', 'feels_like', 'wind_deg', 'wind_speed',
               'wind_gust', 'calculated_at', 'location']

    def query_raw_data(self, run_id) -> Tuple[str, List[str]]:
        base_sql = '''
        SELECT
        lake_id                                     as lake_id
        , data -> 'sys' ->> 'id'                    as sys_id
        , city_id                                   as city_id
        , data -> 'weather' -> 0 ->> 'description'  as description
        , data -> 'main' ->> 'temp'                 as temp
        , data -> 'main' ->> 'humidity'             as humidity
        , data -> 'main' ->> 'pressure'             as pressure
        , data -> 'main' ->> 'temp_max'             as temp_max
        , data -> 'main' ->> 'temp_min'             as temp_min
        , data -> 'main' ->> 'feels_like'           as feels_like
        , data -> 'wind' ->> 'deg'                  as wind_deg
        , data -> 'wind' ->> 'speed'                as wind_speed
        , data -> 'wind' ->> 'gust'                 as wind_gust
        , calculated_at                             as calculated_at
        , location                                  as location
        FROM raw_current_weather
        WHERE run_id = %s
        '''
        return base_sql, [run_id]
