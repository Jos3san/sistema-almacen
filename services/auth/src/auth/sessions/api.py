"""HTTP endpoints of sessions: login, refresh and logout (HU-01 to HU-03)."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from auth.config import get_settings
from auth.db import get_session
from auth.sessions import service
from auth.sessions.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/v1", tags=["sessions"])

DbSession = Annotated[Session, Depends(get_session)]
_UNAUTHORIZED = {401: {"description": "Invalid credentials or session"}}


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    """Send the refresh token in a cookie JavaScript cannot read (docs/06 D1.3)."""
    settings = get_settings()
    response.set_cookie(
        settings.refresh_cookie_name,
        refresh_token,
        max_age=settings.refresh_token_days * 24 * 3600,
        path=settings.refresh_cookie_path,
        secure=True,
        httponly=True,
        samesite="strict",
    )


def _clear_refresh_cookie(response: Response) -> None:
    """Delete the refresh cookie in the browser."""
    settings = get_settings()
    response.delete_cookie(
        settings.refresh_cookie_name,
        path=settings.refresh_cookie_path,
        secure=True,
        httponly=True,
        samesite="strict",
    )


@router.post("/login", responses=_UNAUTHORIZED)
def login(body: LoginRequest, response: Response, session: DbSession) -> TokenResponse:
    """Sign in with email and password (HU-01).

    Returns the access token (15 minutes) and sets the refresh cookie. Any
    failure answers the same 401, so it does not reveal whether the email exists.
    After 5 wrong passwords in a row the user is locked for 15 minutes.
    """
    try:
        issued = service.login(session, body.email, body.password, datetime.now(UTC))
    except service.InvalidCredentialsError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password") from None
    _set_refresh_cookie(response, issued.refresh_token)
    return TokenResponse(access_token=issued.access_token, expires_in=issued.expires_in)


@router.post("/refresh", responses=_UNAUTHORIZED)
def refresh(request: Request, response: Response, session: DbSession) -> TokenResponse:
    """Get a new access token with the refresh cookie, which is rotated (HU-02).

    The new access token carries the user's current permissions.
    """
    token = request.cookies.get(get_settings().refresh_cookie_name)
    try:
        if not token:
            raise service.InvalidRefreshTokenError
        issued = service.refresh(session, token, datetime.now(UTC))
    except service.InvalidRefreshTokenError:
        error = HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expired")
        _clear_refresh_cookie(response)
        error.headers = {"set-cookie": response.headers["set-cookie"]}
        raise error from None
    _set_refresh_cookie(response, issued.refresh_token)
    return TokenResponse(access_token=issued.access_token, expires_in=issued.expires_in)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, session: DbSession) -> None:
    """Close the session: revoke the refresh token and delete its cookie (HU-03)."""
    token = request.cookies.get(get_settings().refresh_cookie_name)
    service.logout(session, token, datetime.now(UTC))
    _clear_refresh_cookie(response)
