"""Tables of users, profiles and permissions (docs/03, docs/06 D2)."""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from auth.db import Base


class User(Base):
    """A person who signs in. The email is stored in lowercase and is unique."""

    __tablename__ = "users"
    __table_args__ = (CheckConstraint("email = lower(email)", name="email_lowercase"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str]
    active: Mapped[bool] = mapped_column(default=True)
    failed_logins: Mapped[int] = mapped_column(default=0)
    locked_until: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Permission(Base):
    """A permission code such as "order.create" (docs/06 D2)."""

    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    description: Mapped[str]


class Profile(Base):
    """A default bundle of permissions: owner, seller, warehouse, courier."""

    __tablename__ = "profiles"

    code: Mapped[str] = mapped_column(String(30), primary_key=True)
    name: Mapped[str] = mapped_column(String(60))


class ProfilePermission(Base):
    """Which permissions each profile includes."""

    __tablename__ = "profile_permissions"

    profile_code: Mapped[str] = mapped_column(ForeignKey("profiles.code"), primary_key=True)
    permission_code: Mapped[str] = mapped_column(ForeignKey("permissions.code"), primary_key=True)


class UserProfile(Base):
    """Profiles assigned to a user (a user can have several)."""

    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    profile_code: Mapped[str] = mapped_column(ForeignKey("profiles.code"), primary_key=True)


class UserPermission(Base):
    """Extra permissions given to one user, on top of their profiles."""

    __tablename__ = "user_permissions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    permission_code: Mapped[str] = mapped_column(ForeignKey("permissions.code"), primary_key=True)
