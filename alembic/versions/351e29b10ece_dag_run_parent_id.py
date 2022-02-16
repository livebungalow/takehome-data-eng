"""Dag Runs Parent Run ID Column

Revision ID: 351e29b10ece
Revises: a30c268c41ab
Create Date: 2022-02-15 16:00:20.969780

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '351e29b10ece'
down_revision = 'a30c268c41ab'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('SET SEARCH_PATH TO weather;')  # There's got to be a better way to manage this
    op.add_column('dag_runs', sa.Column('parent_run_id', sa.Integer))


def downgrade():
    op.execute('SET SEARCH_PATH TO weather;')  # There's got to be a better way to manage this
    op.drop_column('dag_runs', 'parent_run_id')
