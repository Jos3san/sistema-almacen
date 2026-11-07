"""Configuration of the core service, read from environment variables (docs/06 D1.6)."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings of the core service.

    Each field is read from the environment variable with the same name in
    uppercase (database_url -> DATABASE_URL). A missing required value raises
    a validation error that names it, instead of failing later in odd ways.
    """

    database_url: str


@lru_cache
def get_settings() -> Settings:
    """Read the settings once and reuse them for the whole process."""
    return Settings()
