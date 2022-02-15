"""create postgres t1 targets

Revision ID: a30c268c41ab
Revises: 
Create Date: 2022-02-14 16:33:04.844989

"""
from logging import getLogger
import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = 'a30c268c41ab'
down_revision = None
branch_labels = None
depends_on = None

logger = getLogger(revision)
env = os.environ.get('ENV', '').upper()

t1_table_name = 'raw_current_weather'
dag_runs_table_name = 'dag_runs'
fk_name = f'fk_run_id_{t1_table_name}_{dag_runs_table_name}'


def upgrade():
    # Prior to running this migration, be sure to run permissions.sql
    # And configure the connection in airflow

    op.execute('SET SEARCH_PATH TO weather;')  # There's got to be a better way to manage this
    op.create_table(
        dag_runs_table_name,
        sa.Column('run_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('dag_name', sa.String, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.func.now()),
        sa.Column('status', sa.String),
    )

    logger.info('[+] Creating table %s', t1_table_name)
    op.create_table(
        t1_table_name,
        sa.Column('lake_id', sa.Integer, primary_key=True),
        sa.Column('run_id', sa.Integer, nullable=False),
        sa.Column('ran_at', sa.TIMESTAMP, nullable=False),
        sa.Column('calculated_at', sa.TIMESTAMP),
        sa.Column('location', sa.String),
        sa.Column('city_id', sa.Integer),
        sa.Column('data', JSONB)
    )

    logger.info('[+] Creating FK')
    op.create_foreign_key(
        constraint_name=fk_name,
        source_table=t1_table_name,
        referent_table=dag_runs_table_name,
        local_cols=['run_id'],
        remote_cols=['run_id']
    )


def downgrade():
    op.execute('SET SEARCH_PATH TO weather;')  # There's got to be a better way to manage this

    logger.info('[+] Dropping FK')
    op.drop_constraint(
        constraint_name=fk_name,
        table_name=t1_table_name
    )

    logger.info('[+] Dropping table %s', t1_table_name)
    op.drop_table(t1_table_name)

    logger.info('[+] Dropping table %s', dag_runs_table_name)
    op.drop_table(dag_runs_table_name)
