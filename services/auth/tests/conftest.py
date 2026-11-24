"""Shared fixtures: real PostgreSQL with infra's init scripts, migrations, keys and users."""

import os
import re
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session
from testcontainers.community.postgres import PostgresContainer

SERVICE_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = SERVICE_DIR.parents[1]
INIT_DIR = REPO_DIR / "infra" / "postgres" / "init"
COMPOSE_FILE = REPO_DIR / "infra" / "compose.yaml"
PASSWORD = "contrasena-de-prueba-123"


def _postgres_image() -> str:
    """The PostgreSQL image of infra/compose.yaml (one version to maintain)."""
    match = re.search(r"image:\s*(postgres:\S+)", COMPOSE_FILE.read_text(encoding="utf-8"))
    assert match, "No postgres image in compose.yaml"
    return match.group(1)


@pytest.fixture(scope="session")
def private_key() -> rsa.RSAPrivateKey:
    """A throwaway key pair standing in for infra/secrets."""
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(scope="session")
def database_urls(tmp_path_factory, private_key) -> Iterator[dict[str, str]]:
    """Start PostgreSQL with infra's scripts, migrate auth_db and configure the service."""
    container = (
        PostgresContainer(
            _postgres_image(), username="postgres", password="admin", driver="psycopg"
        )
        .with_env("CORE_OWNER_PASSWORD", "core-owner")
        .with_env("CORE_APP_PASSWORD", "core-app")
        .with_env("AUTH_OWNER_PASSWORD", "owner")
        .with_env("AUTH_APP_PASSWORD", "app")
        .with_volume_mapping(str(INIT_DIR), "/docker-entrypoint-initdb.d", "ro")
    )
    with container as postgres:
        address = f"{postgres.get_container_host_ip()}:{postgres.get_exposed_port(5432)}"
        urls = {
            "owner": f"postgresql+psycopg://auth_owner:owner@{address}/auth_db",
            "app": f"postgresql+psycopg://auth_app:app@{address}/auth_db",
        }
        key_path = tmp_path_factory.mktemp("keys") / "jwt_private.pem"
        key_path.write_bytes(
            private_key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
        os.environ.update(
            {
                "MIGRATION_DATABASE_URL": urls["owner"],
                "DATABASE_URL": urls["app"],
                "JWT_PRIVATE_KEY_PATH": str(key_path),
                # TestClient calls /v1/... directly (no gateway), so the cookie path is /v1.
                "REFRESH_COOKIE_PATH": "/v1",
            }
        )
        command.upgrade(Config(str(SERVICE_DIR / "alembic.ini")), "head")
        yield urls


@pytest.fixture
def client(database_urls) -> Iterator[TestClient]:
    """HTTPS test client (Secure cookies are only sent over HTTPS), with empty tables."""
    from auth.config import get_settings
    from auth.db import get_engine
    from auth.main import app
    from auth.sessions import tokens

    get_settings.cache_clear()
    get_engine.cache_clear()
    tokens._private_key.cache_clear()
    _delete_users(database_urls["app"])
    yield TestClient(app, base_url="https://testserver")


@pytest.fixture
def create_user(database_urls) -> Callable[..., str]:
    """Return a function that creates a user (as the app role) and returns its id."""
    from auth.users import passwords
    from auth.users import repository as users_repo
    from auth.users.models import User

    def _create(email="vendedor@example.com", name="Vendedor Ejemplo", profiles=("seller",),
                active=True, password=PASSWORD) -> str:  # fmt: skip
        engine = create_engine(database_urls["app"])
        with Session(engine) as session, session.begin():
            user = User(
                email=email,
                name=name,
                password_hash=passwords.hash_password(password),
                active=active,
            )
            users_repo.add(session, user, list(profiles))
            user_id = str(user.id)
        engine.dispose()
        return user_id

    return _create


def _delete_users(app_url: str) -> None:
    """Empty the user tables between tests (the app role may delete rows, not truncate)."""
    from auth.sessions.models import RefreshToken
    from auth.users.models import User, UserPermission, UserProfile

    engine = create_engine(app_url)
    with Session(engine) as session, session.begin():
        for table in (RefreshToken, UserPermission, UserProfile, User):
            session.execute(delete(table))
    engine.dispose()
