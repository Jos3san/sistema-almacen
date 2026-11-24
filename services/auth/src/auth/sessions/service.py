"""Business rules of sessions: login, refresh and logout (HU-01 to HU-03, docs/06 D1.3).

This layer knows nothing about HTTP: it raises domain errors and the api layer
turns them into 401 responses (docs/06 D1.11).
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from auth.config import get_settings
from auth.sessions import repository as sessions_repo
from auth.sessions import tokens
from auth.sessions.models import RefreshToken
from auth.users import passwords
from auth.users import repository as users_repo
from auth.users.models import User

logger = logging.getLogger(__name__)


class InvalidCredentialsError(Exception):
    """Wrong email or password, inactive or locked user: always the same error."""


class InvalidRefreshTokenError(Exception):
    """Missing, unknown, expired, revoked or reused refresh token."""


@dataclass(frozen=True)
class IssuedTokens:
    """What a successful login or refresh returns."""

    access_token: str
    refresh_token: str
    expires_in: int
    refresh_token_id: uuid.UUID


def login(session: Session, email: str, password: str, now: datetime) -> IssuedTokens:
    """Check the credentials and issue tokens, applying the lockout rule (HU-01)."""
    issued = None
    with session.begin():
        user = users_repo.find_by_email_for_update(session, email.strip().lower())
        if _credentials_ok(user, password, now):
            issued = _issue_tokens(session, user, now)
    # The transaction is committed first, so failed attempts are counted.
    if issued is None:
        raise InvalidCredentialsError
    return issued


def refresh(session: Session, refresh_token: str, now: datetime) -> IssuedTokens:
    """Exchange a refresh token for new tokens, rotating it (HU-02).

    Using a token that was already rotated means it was stolen: every session
    of that user is revoked.
    """
    issued = None
    with session.begin():
        stored = sessions_repo.find_by_hash_for_update(
            session, tokens.hash_refresh_token(refresh_token)
        )
        if stored is not None and stored.revoked_at is not None:
            logger.warning(
                "Refresh token reused: revoking all sessions",
                extra={"fields": {"user_id": str(stored.user_id)}},
            )
            sessions_repo.revoke_all_of_user(session, stored.user_id, now)
        elif stored is not None and stored.expires_at > now:
            user = users_repo.get(session, stored.user_id)
            if user is not None and user.active:
                issued = _issue_tokens(session, user, now)
                stored.revoked_at = now
                stored.replaced_by = issued.refresh_token_id
            else:
                sessions_repo.revoke_all_of_user(session, stored.user_id, now)
    if issued is None:
        raise InvalidRefreshTokenError
    return issued


def logout(session: Session, refresh_token: str | None, now: datetime) -> None:
    """Revoke the refresh token, if there is one (HU-03). Calling it twice is harmless."""
    if not refresh_token:
        return
    with session.begin():
        stored = sessions_repo.find_by_hash_for_update(
            session, tokens.hash_refresh_token(refresh_token)
        )
        if stored is not None and stored.revoked_at is None:
            stored.revoked_at = now


def _credentials_ok(user: User | None, password: str, now: datetime) -> bool:
    """Apply HU-01: unknown, inactive or locked users fail; wrong passwords count towards lockout.

    Every failing path still verifies a password, so all of them take the same
    time and the response does not reveal which emails exist.
    """
    if user is None or not user.active or (user.locked_until and user.locked_until > now):
        passwords.verify(None, password)
        return False
    if not passwords.verify(user.password_hash, password):
        _register_failed_login(user, now)
        return False
    user.failed_logins = 0
    user.locked_until = None
    if passwords.needs_rehash(user.password_hash):
        user.password_hash = passwords.hash_password(password)
    return True


def _register_failed_login(user: User, now: datetime) -> None:
    """Count a wrong password; at the limit, lock the user for a while (docs/06 D1.3)."""
    settings = get_settings()
    user.failed_logins += 1
    if user.failed_logins >= settings.max_failed_logins:
        user.locked_until = now + timedelta(minutes=settings.lockout_minutes)
        user.failed_logins = 0
        logger.warning(
            "User locked after failed logins", extra={"fields": {"user_id": str(user.id)}}
        )


def _issue_tokens(session: Session, user: User, now: datetime) -> IssuedTokens:
    """Create an access token with the user's current permissions and a new refresh token."""
    settings = get_settings()
    permissions = users_repo.permission_codes(session, user.id)
    raw_refresh = tokens.new_refresh_token()
    stored = RefreshToken(
        user_id=user.id,
        token_hash=tokens.hash_refresh_token(raw_refresh),
        expires_at=now + timedelta(days=settings.refresh_token_days),
    )
    sessions_repo.add(session, stored)
    return IssuedTokens(
        access_token=tokens.access_token(str(user.id), user.name, permissions, now),
        refresh_token=raw_refresh,
        expires_in=settings.access_token_minutes * 60,
        refresh_token_id=stored.id,
    )
