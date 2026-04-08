import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Allow importing project modules from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import get_settings
from src.database import Base
# Import models so Alembic can detect them for autogenerate
import src.models.client  # noqa: F401
import src.models.vehicle  # noqa: F401

# Alembic Config object
config = context.config

# Set DB URL from project settings (overrides alembic.ini value)
config.set_main_option("sqlalchemy.url", get_settings().DATABASE_URL)

# Configure logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate support
target_metadata = Base.metadata

# Schema to track (only manage tables in sto_khnu schema)
SCHEMA_NAME = "sto_khnu"


def include_object(object, name, type_, reflected, compare_to):
    """Filter: only track objects in sto_khnu schema."""
    if type_ == "table":
        return object.schema == SCHEMA_NAME
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
