"""Tests for GET /v1/me: core validates tokens with auth's public key (T-11, ADR-0007).

The 401/403 rules themselves are tested in libs/security; here we check that
core is wired to them with its settings (issuer "auth", audience "almacen").
"""

import time
from collections.abc import Iterator

import jwt
import pytest
from almacen_security import TokenValidator
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from core.main import app
from core.security import get_token_validator


@pytest.fixture(scope="module")
def private_key() -> rsa.RSAPrivateKey:
    """A throwaway key pair standing in for auth's keys."""
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def client(private_key, tmp_path) -> Iterator[TestClient]:
    """A test client whose validator uses the matching public key, like core in Compose."""
    public_key_path = tmp_path / "jwt_public.pem"
    public_key_path.write_bytes(
        private_key.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )
    validator = TokenValidator(public_key_path, issuer="auth", audience="almacen")
    app.dependency_overrides[get_token_validator] = lambda: validator
    yield TestClient(app)
    app.dependency_overrides.clear()


def token(private_key, **overrides) -> str:
    """Sign an access token like auth does; keyword arguments change claims."""
    now = int(time.time())
    claims = {
        "sub": "user-1",
        "name": "Usuario Ejemplo",
        "perms": ["stock.read", "order.create"],
        "iss": "auth",
        "aud": "almacen",
        "iat": now,
        "exp": now + 900,
    } | overrides
    return jwt.encode(claims, private_key, algorithm="RS256")


def test_me_without_token_is_401(client):
    """No token: 401."""
    assert client.get("/v1/me").status_code == 401


def test_me_with_expired_token_is_401(client, private_key):
    """An expired token: 401."""
    past = int(time.time()) - 60
    expired = token(private_key, iat=past - 900, exp=past)

    response = client.get("/v1/me", headers={"Authorization": f"Bearer {expired}"})

    assert response.status_code == 401


def test_me_with_valid_token_returns_the_user(client, private_key):
    """A valid token: 200 with the user taken from the token, permissions sorted."""
    response = client.get("/v1/me", headers={"Authorization": f"Bearer {token(private_key)}"})

    assert response.status_code == 200
    assert response.json() == {
        "user_id": "user-1",
        "name": "Usuario Ejemplo",
        "permissions": ["order.create", "stock.read"],
    }
