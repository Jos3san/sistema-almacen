"""initial empty revision

Revision ID: 638f43de08c5
Revises:
Create Date: 2026-11-14 10:13:15.839944
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision: str = "638f43de08c5"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply this change to the schema."""
    pass


def downgrade() -> None:
    """Undo this change."""
    pass
