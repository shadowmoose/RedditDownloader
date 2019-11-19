from logging import basicConfig, INFO

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import sys
from os import path
dr = path.abspath(path.dirname(path.abspath(__file__)))
sys.path.insert(0, path.abspath(path.join(dr, '../../')))

"""
    TO RUN MIGRATIONS:
        alembic -x dbPath=../path-to/sqlite.sqlite revision --autogenerate -m "Message"
        alembic -x dbPath=../path-to/sqlite.sqlite upgrade head
"""

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
# fileConfig(config.config_file_name)
basicConfig(level=INFO, format='%(levelname)-5.5s [%(name)s] %(message)s', datefmt='%H:%M:%S')

# add your model's MetaData object here
# for 'autogenerate' support
import sql
target_metadata = sql.Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    raise Exception('No offline migrations!')


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    ini_section = config.get_section(config.config_ini_section)

    db_path = context.get_x_argument(as_dictionary=True).get('dbPath')
    if db_path:
        ini_section['sqlalchemy.url'] += db_path

    connectable = config.attributes.get('connection', None)

    if connectable is None:
        # only create Engine if we don't have a Connection
        # from the outside
        connectable = engine_from_config(
            config.get_section(config.config_ini_section),
            prefix='sqlalchemy.',
            poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, render_as_batch=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
