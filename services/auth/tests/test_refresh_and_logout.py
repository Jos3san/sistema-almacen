"""Tests for POST /v1/refresh and POST /v1/logout (HU-02, HU-03, docs/06 D1.3)."""

from datetime import UTC, datetime, timedelta

from conftest import PASSWORD
from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session

from auth.sessions.models import RefreshToken
from auth.users.models import UserPermission


def login_cookie(client) -> str:
    """Sign in and return the refresh token sent in the cookie."""
    response = client.post(
        "/v1/login", json={"email": "vendedor@example.com", "password": PASSWORD}
    )
    assert response.status_code == 200
    return response.cookies["refresh_token"]


def refresh_with(client, refresh_token: str | None):
    """Call /v1/refresh sending exactly this cookie (or none)."""
    client.cookies.clear()
    headers = {"Cookie": f"refresh_token={refresh_token}"} if refresh_token else {}
    return client.post("/v1/refresh", headers=headers)


def test_refresh_returns_new_access_token_and_rotates_the_cookie(client, create_user):
    """Each refresh gives a new access token and a NEW refresh token."""
    create_user()
    first = login_cookie(client)

    response = refresh_with(client, first)

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.cookies["refresh_token"] != first


def test_reusing_a_rotated_refresh_token_revokes_every_session(client, create_user):
    """A rotated token used again means it was stolen: all the user's sessions end."""
    create_user()
    first = login_cookie(client)
    second = refresh_with(client, first).cookies["refresh_token"]

    reuse = refresh_with(client, first)

    assert reuse.status_code == 401
    assert refresh_with(client, second).status_code == 401


def test_refresh_without_cookie_is_401(client):
    """No cookie: 401."""
    assert refresh_with(client, None).status_code == 401


def test_unknown_refresh_token_is_401_and_clears_the_cookie(client):
    """An invented token is rejected and the browser is told to delete the cookie."""
    response = refresh_with(client, "token-inventado")

    assert response.status_code == 401
    assert 'refresh_token=""' in response.headers["set-cookie"]


def test_expired_refresh_token_is_401(client, create_user, database_urls):
    """After 7 days without use the session ends."""
    create_user()
    token = login_cookie(client)
    _run(database_urls, update(RefreshToken).values(expires_at=datetime.now(UTC) - timedelta(1)))

    assert refresh_with(client, token).status_code == 401


def test_refresh_carries_the_current_permissions(client, create_user, database_urls):
    """A permission given after login appears in the next access token (max. 15 minutes)."""
    import jwt

    user_id = create_user()
    token = login_cookie(client)
    _run(database_urls, UserPermission.__table__.insert().values(
        user_id=user_id, permission_code="price.edit"))  # fmt: skip

    access = refresh_with(client, token).json()["access_token"]

    assert "price.edit" in jwt.decode(access, options={"verify_signature": False})["perms"]


def test_logout_revokes_the_refresh_token_and_deletes_the_cookie(client, create_user):
    """After logout the refresh token no longer works (HU-03)."""
    create_user()
    token = login_cookie(client)

    client.cookies.clear()
    response = client.post("/v1/logout", headers={"Cookie": f"refresh_token={token}"})

    assert response.status_code == 204
    assert 'refresh_token=""' in response.headers["set-cookie"]
    assert refresh_with(client, token).status_code == 401


def test_logout_without_session_is_harmless(client):
    """Logging out twice, or without a cookie, still answers 204."""
    client.cookies.clear()
    assert client.post("/v1/logout").status_code == 204


def _run(database_urls, statement) -> None:
    """Run one statement as the app role."""
    engine = create_engine(database_urls["app"])
    with Session(engine) as session, session.begin():
        session.execute(statement)
    engine.dispose()
