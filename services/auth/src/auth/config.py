"""Configuration of the auth service, read from environment variables (docs/06 D1.6)."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings of the auth service (DATABASE_URL, JWT_PRIVATE_KEY_PATH...)."""

    database_url: str
    # Private key that signs access tokens; only auth has it (ADR-0007).
    jwt_private_key_path: Path
    jwt_issuer: str = "auth"
    jwt_audience: str = "almacen"
    access_token_minutes: int = 15
    refresh_token_days: int = 7
    # Login lockout (docs/06 D1.3): 5 failed attempts in a row lock for 15 minutes.
    max_failed_logins: int = 5
    lockout_minutes: int = 15
    # The refresh cookie is only sent to /api/auth/v1 (refresh and logout).
    refresh_cookie_name: str = "refresh_token"
    refresh_cookie_path: str = "/api/auth/v1"


@lru_cache
def get_settings() -> Settings:
    """Read the settings once and reuse them for the whole process."""
    return Settings()
