"""Test fixtures: a throwaway RSA key pair and a factory of signed tokens."""

import time
from collections.abc import Callable
from pathlib import Path

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

ISSUER = "auth"
AUDIENCE = "almacen"


def _new_private_key() -> rsa.RSAPrivateKey:
    """Generate a fresh RSA private key for tests (never a real one)."""
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(scope="session")
def private_key() -> rsa.RSAPrivateKey:
    """The private key auth would use to sign tokens."""
    return _new_private_key()


@pytest.fixture(scope="session")
def other_private_key() -> rsa.RSAPrivateKey:
    """A different private key: tokens signed with it must be rejected."""
    return _new_private_key()


@pytest.fixture(scope="session")
def public_key_path(private_key, tmp_path_factory) -> Path:
    """Write the matching public key to a file, as it is mounted in the containers."""
    pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    path = tmp_path_factory.mktemp("keys") / "jwt_public.pem"
    path.write_bytes(pem)
    return path


@pytest.fixture
def make_token(private_key) -> Callable[..., str]:
    """Return a function that signs a token; keyword arguments change or remove claims."""

    def _make(key=None, algorithm="RS256", **overrides) -> str:
        now = int(time.time())
        claims = {
            "sub": "user-1",
            "name": "Usuario Ejemplo",
            "perms": ["order.create"],
            "iss": ISSUER,
            "aud": AUDIENCE,
            "iat": now,
            "exp": now + 900,
        }
        claims.update(overrides)
        claims = {name: value for name, value in claims.items() if value is not None}
        return jwt.encode(claims, key or private_key, algorithm=algorithm)

    return _make
