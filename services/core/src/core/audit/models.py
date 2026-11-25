"""Table of the audit log. core_app can only INSERT and SELECT it (docs/09, RNF-05)."""

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Identity, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base


class AuditLog(Base):
    """One change: who (copied from the token), what, when, and the data before and after."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    occurred_at: Mapped[datetime] = mapped_column(server_default=func.now())
    user_id: Mapped[str] = mapped_column(String(64))
    user_name: Mapped[str] = mapped_column(String(120))
    action: Mapped[str] = mapped_column(String(40))
    entity: Mapped[str] = mapped_column(String(40))
    entity_id: Mapped[str] = mapped_column(String(40))
    before: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    after: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
