"""Database connection of the core service (SQLAlchemy 2 + psycopg, PostgreSQL)."""

from functools import lru_cache

from sqlalchemy import Engine, create_engine

from core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    """Create the connection pool once and reuse it for the whole process.

    pool_pre_ping discards dead connections (e.g. after a database restart).
    connect_timeout stops a request from hanging when the database is down.
    """
    return create_engine(
        get_settings().database_url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 3},
    )
