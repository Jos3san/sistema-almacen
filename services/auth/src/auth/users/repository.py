"""Database queries about users and their permissions."""

import uuid

from sqlalchemy import select, union
from sqlalchemy.orm import Session

from auth.users.models import ProfilePermission, User, UserPermission, UserProfile


def find_by_email_for_update(session: Session, email: str) -> User | None:
    """Find a user by email and lock the row, so two logins cannot race on the counters."""
    return session.scalar(select(User).where(User.email == email).with_for_update())


def get(session: Session, user_id: uuid.UUID) -> User | None:
    """Find a user by id."""
    return session.get(User, user_id)


def permission_codes(session: Session, user_id: uuid.UUID) -> list[str]:
    """All permission codes of a user: those of their profiles plus the extra ones, sorted."""
    from_profiles = (
        select(ProfilePermission.permission_code)
        .join(UserProfile, UserProfile.profile_code == ProfilePermission.profile_code)
        .where(UserProfile.user_id == user_id)
    )
    extra = select(UserPermission.permission_code).where(UserPermission.user_id == user_id)
    return sorted(session.scalars(union(from_profiles, extra)))


def owner_exists(session: Session) -> bool:
    """Tell whether any active user has the owner profile (used by the bootstrap command)."""
    query = (
        select(User.id)
        .join(UserProfile, UserProfile.user_id == User.id)
        .where(UserProfile.profile_code == "owner", User.active.is_(True))
        .limit(1)
    )
    return session.scalar(query) is not None


def add(session: Session, user: User, profile_codes: list[str]) -> None:
    """Insert a user with their profiles."""
    session.add(user)
    session.flush()
    session.add_all(UserProfile(user_id=user.id, profile_code=code) for code in profile_codes)
