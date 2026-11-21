"""Tests for the JSON logs: request id present, sensitive data absent (docs/06 D1.7)."""

import json
import logging
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from core.config import get_settings
from core.db import get_engine
from core.logging_config import JsonFormatter
from core.main import app

client = TestClient(app)


class _JsonLinesHandler(logging.Handler):
    """Keep each log record as the JSON line the service would write to stdout.

    It formats while the request is being handled, like the real handler, so
    the request id is available.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setFormatter(JsonFormatter())
        self.lines: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        """Store the formatted record."""
        self.lines.append(self.format(record))


def _capture_logs(level: int) -> Iterator[list[str]]:
    """Yield the JSON lines logged by the service at the given level or above."""
    logger = logging.getLogger("core")
    handler = _JsonLinesHandler()
    previous_level = logger.level
    logger.addHandler(handler)
    logger.setLevel(level)
    yield handler.lines
    logger.setLevel(previous_level)
    logger.removeHandler(handler)


@pytest.fixture
def all_logs() -> Iterator[list[str]]:
    """Capture every log line, including DEBUG."""
    yield from _capture_logs(logging.DEBUG)


@pytest.fixture
def normal_logs() -> Iterator[list[str]]:
    """Capture the log lines visible at the level used in production (INFO)."""
    yield from _capture_logs(logging.INFO)


def test_log_line_is_json_with_request_id(all_logs):
    """A request is logged as valid JSON that carries the X-Request-ID sent by the gateway."""
    client.get("/health", headers={"X-Request-ID": "test-id-123"})

    entry = json.loads(all_logs[-1])

    assert entry["request_id"] == "test-id-123"
    assert entry["method"] == "GET"
    assert entry["path"] == "/health"
    assert entry["status"] == 200
    assert "duration_ms" in entry


def test_request_id_is_generated_when_missing(all_logs):
    """Without the header (no gateway, e.g. local development) the service creates an id."""
    client.get("/health")

    assert json.loads(all_logs[-1])["request_id"]


def test_logs_never_contain_token_cookie_or_body(all_logs):
    """The token, the cookie and the request body do not reach the logs (docs/06 D1.7)."""
    client.post(
        "/health",
        headers={"Authorization": "Bearer secret-token", "Cookie": "refresh=secret-cookie"},
        json={"password": "secret-body"},
    )

    output = "\n".join(all_logs)

    assert output, "the request must have been logged"
    assert "secret-token" not in output
    assert "secret-cookie" not in output
    assert "secret-body" not in output


def test_logs_never_contain_query_string(all_logs):
    """The query string can carry personal data (e.g. a search by DNI), so it is not logged."""
    client.get("/health?dni=12345678")

    output = "\n".join(all_logs)

    assert output, "the request must have been logged"
    assert "12345678" not in output


def test_successful_health_checks_stay_out_of_normal_logs(normal_logs):
    """Health checks run every few seconds: at INFO level they would bury everything else."""
    client.get("/health")

    assert normal_logs == []


def test_other_requests_appear_in_normal_logs(normal_logs):
    """Any other request is visible at INFO level, even if it fails."""
    client.get("/does-not-exist")

    assert json.loads(normal_logs[-1])["status"] == 404


def test_database_errors_hide_query_values(monkeypatch):
    """The engine keeps query values (personal data) out of its error messages."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pass@localhost/db")
    monkeypatch.setenv("JWT_PUBLIC_KEY_PATH", "/run/secrets/jwt_public.pem")
    get_settings.cache_clear()
    get_engine.cache_clear()

    assert get_engine().hide_parameters is True

    get_settings.cache_clear()
    get_engine.cache_clear()
