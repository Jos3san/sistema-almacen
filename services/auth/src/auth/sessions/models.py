"""Table of refresh tokens (docs/06 D1.3)."""

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from auth.db import Base


class RefreshToken(Base):
    """One refresh token. Only its SHA-256 hash is stored, never the token itself.

    Each use rotates it: the old one gets revoked_at and points to the new one
    (replaced_by). Presenting a revoked token again means it was stolen.
    """

    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    revoked_at: Mapped[datetime | None]
    replaced_by: Mapped[uuid.UUID | None]
