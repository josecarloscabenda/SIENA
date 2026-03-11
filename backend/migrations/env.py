"""Alembic environment configuration."""

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from src.common.database.base import Base

# Import all models so Alembic can detect them
import src.modules.escolas.infrastructure.models  # noqa: F401
import src.modules.identity.infrastructure.models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

database_url = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://siena:siena@localhost:5432/siena",
)
# Alembic usa driver síncrono
sync_url = database_url.replace("+psycopg", "+psycopg")


def include_name(name, type_, parent_names):  # noqa: ANN001, ARG001
    """Only include tables from our module schemas."""
    if type_ == "schema":
        return name in (
            "identity", "escolas", "directory", "enrollment", "academico",
            "avaliacoes", "financeiro", "provas", "vocacional", "relatorios",
            "estoque", "alimentacao", "integracoes", "sync", "notifications",
        )
    return True


def run_migrations_offline() -> None:
    context.configure(
        url=sync_url,
        target_metadata=target_metadata,
        literal_binds=True,
        include_schemas=True,
        include_name=include_name,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(sync_url)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_name=include_name,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()