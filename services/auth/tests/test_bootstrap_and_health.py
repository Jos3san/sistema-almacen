"""Tests for the first-owner command (HU-05), health endpoints and database roles."""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from auth.bootstrap import create_first_owner


def test_bootstrap_creates_an_owner_who_can_sign_in(client, database_urls):
    """The command creates the owner, who then signs in with every permission."""
    engine = create_engine(database_urls["app"])
    with Session(engine) as session:
        created = create_first_owner(session, "Duenio@Example.com", "Dueño", "clave-larga-segura")
    engine.dispose()

    response = client.post(
        "/v1/login", json={"email": "duenio@example.com", "password": "clave-larga-segura"}
    )

    assert created is True
    assert response.status_code == 200


def test_bootstrap_does_nothing_if_an_owner_exists(client, database_urls):
    """Running it again does not create a second owner."""
    engine = create_engine(database_urls["app"])
    with Session(engine) as session:
        create_first_owner(session, "duenio@example.com", "Dueño", "clave-larga-segura")
    with Session(engine) as session:
        created_again = create_first_owner(session, "otro@example.com", "Otro", "clave-larga-2")
    engine.dispose()

    assert created_again is False


def test_bootstrap_rejects_short_passwords(database_urls):
    """The first owner needs a password of at least 12 characters."""
    engine = create_engine(database_urls["app"])
    with Session(engine) as session, pytest.raises(ValueError):
        create_first_owner(session, "duenio@example.com", "Dueño", "corta")
    engine.dispose()


def test_health_and_readiness(client):
    """/health answers when alive; /health/ready when auth_db answers too."""
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/health/ready").json() == {"status": "ok"}


def test_app_role_cannot_change_the_schema(database_urls):
    """auth_app reads and writes rows but cannot create tables (docs/06 D1.6)."""
    engine = create_engine(database_urls["app"])
    with engine.begin() as connection, pytest.raises(ProgrammingError, match="permission denied"):
        connection.execute(text("CREATE TABLE hack (id int)"))
    engine.dispose()


def test_auth_roles_cannot_reach_core_db(database_urls):
    """Each service only reaches its own database: auth_app cannot connect to core_db."""
    url = database_urls["app"].rsplit("/", 1)[0] + "/core_db"
    engine = create_engine(url)
    with pytest.raises(Exception, match="permission denied"):
        engine.connect()
    engine.dispose()
