"""Configuration of the core service, read from environment variables (docs/06 D1.6)."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings of the core service.

    Each field is read from the environment variable with the same name in
    uppercase (database_url -> DATABASE_URL). A missing required value raises
    a validation error that names it, instead of failing later in odd ways.
    """

    database_url: str
    # auth's public key, mounted as a file; core never calls auth (ADR-0007).
    jwt_public_key_path: Path
    # Who must have issued the tokens and for whom (docs/06 D1.3).
    jwt_issuer: str = "auth"
    jwt_audience: str = "almacen"


@lru_cache
def get_settings() -> Settings:
    """Read the settings once and reuse them for the whole process."""
    return Settings()
