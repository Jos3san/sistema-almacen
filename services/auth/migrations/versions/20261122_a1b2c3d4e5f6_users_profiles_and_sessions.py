"""users, profiles, permissions and refresh tokens, with the default profiles (docs/06 D2)

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-11-22 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Permission catalog of docs/06 D2 (code, description).
PERMISSIONS = [
    ("user.manage", "Crear, editar y desactivar usuarios; asignar perfiles y permisos"),
    ("audit.view", "Consultar la auditoría"),
    ("catalog.manage", "Gestionar productos, categorías, marcas, presentaciones y stock mínimo"),
    ("price.edit", "Crear y cambiar escalas de precio"),
    ("cost.view", "Ver y editar el costo de los productos"),
    ("catalog.import", "Importar productos desde Excel/CSV"),
    ("location.manage", "Crear y editar ubicaciones"),
    ("customer.manage", "Crear y editar clientes"),
    ("supplier.manage", "Crear y editar proveedores"),
    ("inventory.initial_load", "Cargar el inventario inicial de una ubicación"),
    ("stock.read", "Consultar stock, presentaciones y precios"),
    ("stock.receive", "Registrar ingresos de mercadería"),
    ("stock.transfer", "Transferir entre ubicaciones"),
    ("adjustment.request", "Proponer ajustes"),
    ("adjustment.approve", "Aprobar o rechazar ajustes"),
    ("kardex.read", "Consultar el kardex"),
    ("order.read", "Ver todos los pedidos, su estado y su nota de venta"),
    ("order.create", "Crear pedidos"),
    ("order.update", "Modificar pedidos"),
    ("order.close_shortage", "Cerrar lo por conseguir"),
    ("order.cancel", "Anular pedidos"),
    ("payment.register", "Registrar pagos"),
    ("dispatch.prepare", "Ver la bandeja de pendientes y marcar en preparación"),
    ("dispatch.create", "Despachar, asignar repartidor y registrar nº de comprobante"),
    ("dispatch.register_late", "Registrar pedidos y despachos hechos en papel"),
    ("dispatch.deliver", "Marcar en camino y registrar la entrega con rechazos"),
    ("report.view", "Ver reportes"),
    ("report.export", "Exportar reportes a Excel o PDF"),
]

# Default profiles of docs/06 D2 (code, name, permissions). The owner has all of them.
PROFILES = [
    ("owner", "Dueño", [code for code, _ in PERMISSIONS]),
    (
        "seller",
        "Vendedor",
        [
            "customer.manage",
            "stock.read",
            "order.read",
            "order.create",
            "order.update",
            "order.close_shortage",
            "order.cancel",
            "payment.register",
        ],
    ),
    (
        "warehouse",
        "Almacén",
        [
            "stock.read",
            "stock.receive",
            "stock.transfer",
            "adjustment.request",
            "kardex.read",
            "order.read",
            "dispatch.prepare",
            "dispatch.create",
            "dispatch.register_late",
        ],
    ),
    ("courier", "Repartidor", ["stock.read", "payment.register", "dispatch.deliver"]),
]


def upgrade() -> None:
    """Create the tables and load the permission catalog and the 4 default profiles."""
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("failed_logins", sa.Integer(), nullable=False),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("email = lower(email)", name="email_lowercase"),
        sa.CheckConstraint("failed_logins >= 0", name="failed_logins_not_negative"),
    )
    permissions = op.create_table(
        "permissions",
        sa.Column("code", sa.String(50), primary_key=True),
        sa.Column("description", sa.String(), nullable=False),
    )
    profiles = op.create_table(
        "profiles",
        sa.Column("code", sa.String(30), primary_key=True),
        sa.Column("name", sa.String(60), nullable=False),
    )
    profile_permissions = op.create_table(
        "profile_permissions",
        sa.Column("profile_code", sa.String(30), sa.ForeignKey("profiles.code"), primary_key=True),
        sa.Column(
            "permission_code", sa.String(50), sa.ForeignKey("permissions.code"), primary_key=True
        ),
    )
    op.create_table(
        "user_profiles",
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column("profile_code", sa.String(30), sa.ForeignKey("profiles.code"), primary_key=True),
    )
    op.create_table(
        "user_permissions",
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column(
            "permission_code", sa.String(50), sa.ForeignKey("permissions.code"), primary_key=True
        ),
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("replaced_by", sa.Uuid(), nullable=True),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])

    op.bulk_insert(permissions, [{"code": c, "description": d} for c, d in PERMISSIONS])
    op.bulk_insert(profiles, [{"code": c, "name": n} for c, n, _ in PROFILES])
    op.bulk_insert(
        profile_permissions,
        [{"profile_code": c, "permission_code": p} for c, _, perms in PROFILES for p in perms],
    )


def downgrade() -> None:
    """Drop every table of this revision."""
    for table in (
        "refresh_tokens",
        "user_permissions",
        "user_profiles",
        "profile_permissions",
        "profiles",
        "permissions",
        "users",
    ):
        op.drop_table(table)
