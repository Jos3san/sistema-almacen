"""Fixtures shared by every test module of the core service."""

import re
from pathlib import Path

import pytest

COMPOSE_FILE = Path(__file__).resolve().parents[3] / "infra" / "compose.yaml"


@pytest.fixture(scope="session")
def postgres_image() -> str:
    """Return the PostgreSQL image used by infra/compose.yaml.

    Tests read it from there, so they always run against the version used in
    the real environment, and Dependabot updates it in a single place.
    """
    match = re.search(r"image:\s*(postgres:\S+)", COMPOSE_FILE.read_text(encoding="utf-8"))
    if match is None:
        raise RuntimeError(f"No postgres image found in {COMPOSE_FILE}")
    return match.group(1)
