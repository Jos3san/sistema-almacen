"""Creation of access tokens (JWT RS256) and refresh tokens (random strings)."""

import hashlib
import secrets
from datetime import datetime, timedelta
from functools import lru_cache

import jwt

from auth.config import get_settings


@lru_cache
def _private_key() -> str:
    """Read auth's private key once from the mounted file (JWT_PRIVATE_KEY_PATH)."""
    return get_settings().jwt_private_key_path.read_text(encoding="utf-8")


def access_token(user_id: str, name: str, permissions: list[str], now: datetime) -> str:
    """Sign an access token with the claims every service expects (docs/06 D1.3)."""
    settings = get_settings()
    claims = {
        "sub": user_id,
        "name": name,
        "perms": permissions,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_minutes),
    }
    return jwt.encode(claims, _private_key(), algorithm="RS256")


def new_refresh_token() -> str:
    """A long random value (256 bits) that cannot be guessed."""
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str) -> str:
    """SHA-256 of the refresh token: the database only keeps this hash.

    A fast hash is enough here (unlike passwords) because the token is random
    and long, so it cannot be guessed by trying values.
    """
    return hashlib.sha256(token.encode()).hexdigest()
