"""Tests for POST /v1/login (HU-01, docs/06 D1.3)."""

import jwt
from conftest import PASSWORD

GENERIC_ERROR = {"detail": "Invalid email or password"}


def login(client, email="vendedor@example.com", password=PASSWORD):
    """Call the login endpoint."""
    return client.post("/v1/login", json={"email": email, "password": password})


def test_login_returns_access_token_with_profile_permissions(client, create_user, private_key):
    """Correct credentials: a 15-minute RS256 token with the user's permissions."""
    user_id = create_user(profiles=("seller",))

    response = login(client)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 900
    claims = jwt.decode(
        body["access_token"], private_key.public_key(), algorithms=["RS256"], audience="almacen"
    )
    assert claims["sub"] == user_id
    assert claims["iss"] == "auth"
    assert claims["name"] == "Vendedor Ejemplo"
    assert "order.create" in claims["perms"]
    assert "price.edit" not in claims["perms"]
    assert claims["exp"] - claims["iat"] == 900


def test_login_sets_secure_refresh_cookie(client, create_user):
    """The refresh token travels only in an HttpOnly, Secure, SameSite=Strict cookie."""
    create_user()

    response = login(client)

    cookie = response.headers["set-cookie"]
    assert cookie.startswith("refresh_token=")
    assert "HttpOnly" in cookie
    assert "Secure" in cookie
    assert "SameSite=strict" in cookie
    assert "Path=/v1" in cookie
    assert "refresh_token" not in response.json()


def test_email_is_case_insensitive(client, create_user):
    """The email is matched in lowercase."""
    create_user()

    assert login(client, email="  Vendedor@Example.COM ").status_code == 200


def test_wrong_password_and_unknown_email_get_the_same_answer(client, create_user):
    """Both answer 401 with the same message: the response does not reveal which emails exist."""
    create_user()

    wrong_password = login(client, password="otra-contrasena-123")
    unknown_email = login(client, email="nadie@example.com")

    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json() == GENERIC_ERROR


def test_inactive_user_cannot_sign_in(client, create_user):
    """A deactivated user gets the same 401."""
    create_user(active=False)

    response = login(client)

    assert response.status_code == 401
    assert response.json() == GENERIC_ERROR


def test_five_failed_attempts_lock_the_user(client, create_user):
    """After 5 wrong passwords in a row, even the right password fails (15-minute lock)."""
    create_user()
    for _ in range(5):
        assert login(client, password="otra-contrasena-123").status_code == 401

    assert login(client).status_code == 401


def test_a_successful_login_resets_the_failed_attempts(client, create_user):
    """The counter counts attempts in a row: a good login starts it again."""
    create_user()
    for _ in range(4):
        login(client, password="otra-contrasena-123")
    assert login(client).status_code == 200

    for _ in range(4):
        login(client, password="otra-contrasena-123")
    assert login(client).status_code == 200


def test_absurdly_long_password_is_rejected_before_hashing(client):
    """Input limits stop huge payloads (422), so they cannot be used to overload argon2."""
    assert login(client, password="x" * 1000).status_code == 422
