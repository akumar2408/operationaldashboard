from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from sqlalchemy import create_engine
import os

from app.db import Base
from app import models  # noqa

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Build from discrete env vars (RDS/compose)
    POSTGRES_USER = os.getenv("POSTGRES_USER","dashboard")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD","dashboardpw")
    POSTGRES_DB = os.getenv("POSTGRES_DB","dashboard")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST","postgres")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT","5432")
    DATABASE_URL = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

def run_migrations_offline():
    context.configure(url=DATABASE_URL, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    # Build engine directly (no prefix/key confusion)
    connectable = create_engine(DATABASE_URL)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
