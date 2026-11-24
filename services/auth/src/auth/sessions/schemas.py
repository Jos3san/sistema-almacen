"""Request and response bodies of the sessions endpoints."""

from typing import Literal

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Email and password typed by the user. Limits stop absurdly large inputs."""

    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    """The access token goes in the body; the refresh token travels only in a cookie."""

    access_token: str
    # "bearer" is the OAuth token type, not a secret.
    token_type: Literal["bearer"] = "bearer"  # noqa: S105
    expires_in: int = Field(description="Seconds until the access token expires")
