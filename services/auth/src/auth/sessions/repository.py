"""Database queries about refresh tokens."""

import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from auth.sessions.models import RefreshToken


def add(session: Session, token: RefreshToken) -> None:
    """Store a new refresh token (its hash)."""
    session.add(token)
    session.flush()


def find_by_hash_for_update(session: Session, token_hash: str) -> RefreshToken | None:
    """Find a refresh token by its hash and lock it, so it cannot be used twice at once."""
    return session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash).with_for_update()
    )


def revoke_all_of_user(session: Session, user_id: uuid.UUID, now: datetime) -> None:
    """Revoke every active refresh token of a user (stolen token or deactivated user)."""
    session.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=now)
    )
