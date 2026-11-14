"""Tests for the database roles and the Alembic migrations (T-10, docs/06 D1.6).

They start PostgreSQL with the real init script of infra/postgres/init, so what
is tested is exactly what Compose (and later production) runs.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import ProgrammingError
from testcontainers.community.postgres import PostgresContainer

# Same image as infra/compose.yaml.
POSTGRES_IMAGE = "postgres:18.6-trixie"
SERVICE_DIR = Path(__file__).resolve().parents[1]
INIT_DIR = SERVICE_DIR.parents[1] / "infra" / "postgres" / "init"


@pytest.fixture(scope="module")
def database_urls() -> Iterator[dict[str, str]]:
    """Start PostgreSQL with infra's init script and yield one URL per role."""
    container = (
        PostgresContainer(POSTGRES_IMAGE, username="postgres", password="admin", driver="psycopg")
        .with_env("CORE_OWNER_PASSWORD", "owner")
        .with_env("CORE_APP_PASSWORD", "app")
        .with_volume_mapping(str(INIT_DIR), "/docker-entrypoint-initdb.d", "ro")
    )
    with container as postgres:
        address = f"{postgres.get_container_host_ip()}:{postgres.get_exposed_port(5432)}"
        yield {
            "owner": f"postgresql+psycopg://core_owner:owner@{address}/core_db",
            "app": f"postgresql+psycopg://core_app:app@{address}/core_db",
        }


def run_sql(url: str, sql: str) -> list[tuple]:
    """Run one statement as the role in the URL and return its rows (if any)."""
    engine = create_engine(url)
    try:
        with engine.begin() as connection:
            result = connection.execute(text(sql))
            return list(result) if result.returns_rows else []
    finally:
        engine.dispose()


def test_app_role_reads_and_writes_tables_created_by_owner(database_urls):
    """Default privileges: core_app can use every table core_owner creates later."""
    run_sql(database_urls["owner"], "CREATE TABLE probe_rw (id int)")

    run_sql(database_urls["app"], "INSERT INTO probe_rw VALUES (1)")

    assert run_sql(database_urls["app"], "SELECT id FROM probe_rw") == [(1,)]


def test_app_role_cannot_create_tables(database_urls):
    """core_app cannot change the schema: only migrations (core_owner) can."""
    with pytest.raises(ProgrammingError, match="permission denied"):
        run_sql(database_urls["app"], "CREATE TABLE hack (id int)")


def test_app_role_cannot_drop_tables(database_urls):
    """core_app cannot drop a table, even one it can read and write."""
    run_sql(database_urls["owner"], "CREATE TABLE probe_drop (id int)")

    with pytest.raises(ProgrammingError, match="must be owner"):
        run_sql(database_urls["app"], "DROP TABLE probe_drop")


def test_migrations_upgrade_and_downgrade(database_urls, monkeypatch):
    """All migrations apply from scratch and can be undone (alembic upgrade/downgrade)."""
    monkeypatch.setenv("MIGRATION_DATABASE_URL", database_urls["owner"])
    config = Config(str(SERVICE_DIR / "alembic.ini"))

    command.upgrade(config, "head")
    assert "alembic_version" in inspect(create_engine(database_urls["owner"])).get_table_names()

    command.downgrade(config, "base")
    rows = run_sql(database_urls["owner"], "SELECT count(*) FROM alembic_version")
    assert rows == [(0,)]
