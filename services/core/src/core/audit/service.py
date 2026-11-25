"""Record changes in the audit log, inside the caller's transaction."""

from typing import Any

from almacen_security import TokenClaims
from sqlalchemy.orm import Session

from core.audit.models import AuditLog


def record(
    session: Session,
    user: TokenClaims,
    action: str,
    entity: str,
    entity_id: object,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
) -> None:
    """Add one audit entry. It is saved or discarded together with the change it describes.

    The user's id and name come from the token, as a snapshot (docs/06 D1.3):
    core never asks auth who the user is.
    """
    session.add(
        AuditLog(
            user_id=user.user_id,
            user_name=user.name,
            action=action,
            entity=entity,
            entity_id=str(entity_id),
            before=before,
            after=after,
        )
    )
