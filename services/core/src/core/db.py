"""Database connection of the core service (SQLAlchemy 2 + psycopg, PostgreSQL)."""

from collections.abc import Iterator
from datetime import datetime
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy import DateTime, Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from core.config import get_settings


class Base(DeclarativeBase):
    """Base class of every table of core_db.

    Every datetime column is "timestamptz": stored in UTC (docs/09).
    """

    type_annotation_map = {datetime: DateTime(timezone=True)}


@lru_cache
def get_engine() -> Engine:
    """Create the connection pool once and reuse it for the whole process.

    pool_pre_ping discards dead connections (e.g. after a database restart).
    connect_timeout stops a request from hanging when the database is down.
    hide_parameters keeps query values (personal data) out of error messages
    and therefore out of the logs (docs/06 D1.7).
    """
    return create_engine(
        get_settings().database_url,
        pool_pre_ping=True,
        hide_parameters=True,
        connect_args={"connect_timeout": 3},
    )


def get_session(engine: Annotated[Engine, Depends(get_engine)]) -> Iterator[Session]:
    """Give each request its own session; services open the transaction (docs/06 D1.11)."""
    with Session(engine, expire_on_commit=False) as session:
        yield session
