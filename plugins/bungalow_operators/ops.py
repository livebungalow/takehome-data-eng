import logging
from datetime import datetime
from typing import List
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models.baseoperator import BaseOperator
from bungalow_operators import DEFAULT_POSTGRES_CONN_ID

logger = logging.getLogger('bungalow_operators')
logger.setLevel(logging.INFO)


class DagRunOperator(BaseOperator):
    template_fields = ['name', 'status', 'sql']

    def __init__(self, name: str, status: str,
                 sql: str, query_parameters: List = None,
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

    def get_latest_run_id(self, dag_id, status):
        base_sql = '''
        SELECT run_id
        FROM dag_runs
        WHERE dag_name = %s and status = %s
        ORDER BY updated_at desc
        LIMIT 1
        '''
        cur = self.hook.get_conn().cursor()
        cur.execute(base_sql, (dag_id, status.upper()))
        for row in cur:
            run_id = row[0]
            return run_id

    @classmethod
    def start(cls, name, _dag_id, **kwargs):
        raise NotImplementedError('[X] Must use child classmethod')

    @classmethod
    def update_status(cls, name, status, _dag_id, start_task_id, **kwargs):
        raise NotImplementedError('[X] Must use child classmethod')

    def execute(self, context):
        ti = context['task_instance']

        self.hook.run(self.sql, parameters=self.query_parameters)
        # Push run id to xcom for downstream dags
        run_id = self.get_latest_run_id(dag_id=self.dag_id, status=self.status)
        ti.xcom_push(key='run_id', value=run_id)


class FetcherDagRunOperator(DagRunOperator):
    @classmethod
    def start(cls, name, _dag_id, **kwargs):
        base_sql = '''
        INSERT INTO dag_runs (dag_name, created_at, status) VALUES (%s, %s, %s)
        '''
        query_parameters = [_dag_id, datetime.now(), 'RUNNING']
        return cls(name=name, _dag_id=_dag_id, status='RUNNING',
                   sql=base_sql, query_parameters=query_parameters, **kwargs)

    @classmethod
    def update_status(cls, name, status, _dag_id, start_task_id, **kwargs):
        # Jinja templates not quite cooperating, there should be a way to resolve this
        # with an expression and not string manipulation
        run_id_template = f"task_instance.xcom_pull(task_ids='{start_task_id}', key='run_id')"
        base_sql = '''
            UPDATE dag_runs SET updated_at = %s, status = %s
            WHERE run_id = {run_id_template}
            and dag_name = %s
        '''.format(run_id_template='{{' + run_id_template + '}}')

        query_parameters = [datetime.now(), status, _dag_id]
        return cls(name=name, status=status, sql=base_sql,
                   query_parameters=query_parameters, _dag_id=_dag_id, **kwargs)


class TransformerDagRunOperator(DagRunOperator):
    def __init__(self, fetcher_run_id: str = None, fetcher_dag_id: str = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.fetcher_run_id = fetcher_run_id
        self.fetcher_dag_id = fetcher_dag_id

    @classmethod
    def start(cls, name, _dag_id, **kwargs):
        base_sql = '''
        INSERT INTO dag_runs (dag_name, created_at, status, parent_run_id) VALUES (%s, %s, %s, %s)
        '''
        query_parameters = [_dag_id, datetime.now(), 'RUNNING']
        return cls(name=name, _dag_id=_dag_id, status='RUNNING',
                   sql=base_sql, query_parameters=query_parameters, **kwargs)

    @classmethod
    def update_status(cls, name, status, _dag_id, start_task_id, **kwargs):
        # Jinja templates not quite cooperating, there should be a way to resolve this
        # with an expression and not string manipulation
        run_id_template = f"task_instance.xcom_pull(task_ids='{start_task_id}', key='run_id')"
        base_sql = '''
            UPDATE dag_runs SET updated_at = %s, status = %s
            WHERE run_id = {run_id_template}
            and dag_name = %s and parent_run_id = %s
        '''.format(run_id_template='{{' + run_id_template + '}}')

        query_parameters = [datetime.now(), status, _dag_id]
        return cls(name=name, status=status, sql=base_sql,
                   query_parameters=query_parameters, _dag_id=_dag_id, **kwargs)

    def execute(self, context):
        ti = context['task_instance']
        fetcher_run_id = context['params'].get('fetcher_run_id') or self.fetcher_run_id
        if not fetcher_run_id:
            fetcher_run_id = self.get_latest_run_id(dag_id='fetcher', status='SUCCESS')
        self.query_parameters.append(fetcher_run_id)
        ti.xcom_push(key='fetcher_run_id', value=fetcher_run_id)
        super().execute(context)
