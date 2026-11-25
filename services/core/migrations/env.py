"""Alembic environment of the core service: how migrations connect and run (T-10).

Migrations connect as the schema owner (MIGRATION_DATABASE_URL), never as the
application user, which cannot create or alter tables (docs/06 D1.6).
"""

import os

from alembic import context
from sqlalchemy import create_engine, pool

import core.audit.models  # noqa: F401  (registers the tables in Base.metadata)
import core.catalog.models  # noqa: F401
from core.db import Base
from core.logging_config import configure_logging

configure_logging()

# Table definitions, used by --autogenerate to compare with the database.
target_metadata = Base.metadata


def migration_url() -> str:
    """Return the schema owner's database URL, failing with a clear message if missing."""
    url = os.environ.get("MIGRATION_DATABASE_URL")
    if not url:
        raise RuntimeError("Set MIGRATION_DATABASE_URL to the schema owner's database URL")
    return url


def run_migrations_offline() -> None:
    """Write the migrations as SQL instead of running them (alembic upgrade --sql)."""
    context.configure(url=migration_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Connect to the database and apply the pending migrations in one transaction."""
    engine = create_engine(migration_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
