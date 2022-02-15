import logging
from datetime import datetime
from typing import Tuple
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models.baseoperator import BaseOperator
from bungalow_operators import DEFAULT_POSTGRES_CONN_ID

logger = logging.getLogger('bungalow_operators')
logger.setLevel(logging.INFO)


class DagRunOperator(BaseOperator):
    template_fields = ['name', 'status', 'sql']

    def __init__(self, name: str, status: str,
                 sql: str, query_parameters: Tuple = None,
                 _dag_id: str = None, conn_id: str = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = name
        self._dag_id = _dag_id
        self.status = status
        if status not in ['RUNNING', 'SUCCESS', 'FAILURE']:
            raise ValueError('[X] Unsupported status %s', status)
        self.hook = PostgresHook(postgres_conn_id=conn_id or DEFAULT_POSTGRES_CONN_ID)
        self.sql = sql
        self.query_parameters = query_parameters

    def __repr__(self):
        return self.name

    @classmethod
    def start(cls, name, _dag_id, **kwargs):
        base_sql = '''
        INSERT INTO dag_runs (dag_name, created_at, status) VALUES (%s, %s, %s)
        '''
        query_parameters = (_dag_id, datetime.now(), 'RUNNING')
        return cls(name=name, _dag_id=_dag_id, status='RUNNING',
                   sql=base_sql, query_parameters=query_parameters, **kwargs)

    @classmethod
    def update_status(cls, name, status, _dag_id, **kwargs):
        base_sql = '''
        UPDATE dag_runs SET updated_at = %s, status = %s
        WHERE run_id = {{ task_instance.xcom_pull(task_ids='ops_dag_run_init', key='run_id') }}
            and dag_name = %s
        '''
        query_parameters = (datetime.now(), status, _dag_id)
        return cls(name=name, status=status, sql=base_sql,
                   query_parameters=query_parameters, _dag_id=_dag_id, **kwargs)

    def get_in_progress_run_id(self):
        base_sql = '''
        SELECT run_id
        FROM dag_runs
        WHERE dag_name = %s and status = %s
        ORDER BY updated_at desc
        LIMIT 1
        '''
        cur = self.hook.get_conn().cursor()
        cur.execute(base_sql, (self.dag_id, 'RUNNING'))
        for row in cur:
            run_id = row[0]
            return run_id

    def execute(self, context):
        ti = context['task_instance']

        self.hook.run(self.sql, parameters=self.query_parameters)
        if self.status == 'RUNNING':
            run_id = self.get_in_progress_run_id()
            ti.xcom_push(key='run_id', value=run_id)

        elif self.status == 'FAILURE':
            # If this was integrated elsewhere, like slack, send notifications of failure
            pass
