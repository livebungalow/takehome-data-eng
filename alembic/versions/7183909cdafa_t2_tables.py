"""'t2_tables'

Revision ID: 7183909cdafa
Revises: 351e29b10ece
Create Date: 2022-02-15 16:14:33.430196

"""
from alembic import op
import sqlalchemy as sa
from logging import getLogger

# revision identifiers, used by Alembic.
revision = '7183909cdafa'
down_revision = '351e29b10ece'
branch_labels = None
depends_on = None

logger = getLogger(revision)

t2_cities_tablename = 't2_cities'
t2_weather_tablename = 't2_weather'


def upgrade():
    op.execute('SET SEARCH_PATH TO weather;')  # There's got to be a better way to manage this
    op.create_table(
        t2_cities_tablename,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('city_id', sa.Integer, unique=True),
        sa.Column('lake_id', sa.Integer, nullable=False),
        sa.Column('country', sa.String, nullable=False),
        sa.Column('timezone', sa.Integer),
        sa.Column('lat', sa.Float),
        sa.Column('lon', sa.Float),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        t2_weather_tablename,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('sys_id', sa.Integer, nullable=False, unique=True),
        sa.Column('lake_id', sa.Integer, nullable=False),
        sa.Column('city_id', sa.Integer, nullable=False),
        sa.Column('calculated_at', sa.TIMESTAMP, nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('temp', sa.Float),
        sa.Column('humidity', sa.Float),
        sa.Column('pressure', sa.Float),
        sa.Column('temp_max', sa.Float),
        sa.Column('temp_min', sa.Float),
        sa.Column('feels_like', sa.Float),
        sa.Column('wind_deg', sa.Float),
        sa.Column('wind_speed', sa.Float),
        sa.Column('wind_gust', sa.Float),

        # Columns propagated for debugging
        sa.Column('location', sa.Text)
    )


def downgrade():
    op.execute('SET SEARCH_PATH TO weather;')  # There's got to be a better way to manage this
    logger.info('[+] Dropping table %s', t2_weather_tablename)
    op.drop_table(t2_weather_tablename)

    logger.info('[+] Dropping table %s', t2_cities_tablename)
    op.drop_table(t2_cities_tablename)
