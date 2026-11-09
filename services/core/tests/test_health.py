"""Tests for the /health endpoint."""

from fastapi.testclient import TestClient

from core.main import app

client = TestClient(app)


def test_health_returns_ok():
    """GET /health answers 200 with {"status": "ok"}."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "roto"}
