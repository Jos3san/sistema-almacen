"""Tests for the /health/ready endpoint against a real PostgreSQL (Testcontainers)."""

from collections.abc import Callable, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from testcontainers.community.postgres import PostgresContainer

from core.db import get_engine
from core.main import app

# Same image as infra/compose.yaml: tests run against the version used in production.
POSTGRES_IMAGE = "postgres:18.6-trixie"


@pytest.fixture(scope="module")
def postgres_url() -> Iterator[str]:
    """Start a throwaway PostgreSQL container for this module and yield its URL."""
    with PostgresContainer(POSTGRES_IMAGE, driver="psycopg") as postgres:
        yield postgres.get_connection_url()


@pytest.fixture
def client_for() -> Iterator[Callable[[str], TestClient]]:
    """Give a function that returns a test client whose app uses the given database URL.

    It replaces the app's get_engine dependency and restores it after the test.
    """

    def _client_for(database_url: str) -> TestClient:
        engine = create_engine(database_url, connect_args={"connect_timeout": 3})
        app.dependency_overrides[get_engine] = lambda: engine
        return TestClient(app)

    yield _client_for
    app.dependency_overrides.clear()


def test_ready_ok_when_database_reachable(postgres_url, client_for):
    """GET /health/ready answers 200 when the database answers a query."""
    response = client_for(postgres_url).get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_503_when_database_down(client_for):
    """GET /health/ready answers 503 with no internal details when the database is down."""
    unreachable = "postgresql+psycopg://nobody:wrong@127.0.0.1:1/none"

    response = client_for(unreachable).get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
