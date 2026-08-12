"""accounts table

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-09
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=72), nullable=False),
        sa.Column(
            "role", sa.String(length=20), nullable=False, server_default="parent"
        ),
        sa.Column(
            "approval_status",
            sa.String(length=20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint(
            "role IN ('parent', 'administrator')",
            name="ck_accounts_role",
        ),
        sa.CheckConstraint(
            "approval_status IN ('pending', 'approved', 'rejected')",
            name="ck_accounts_approval_status",
        ),
        sa.ForeignKeyConstraint(
            ["approved_by"],
            ["accounts.id"],
            name="fk_accounts_approved_by",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_accounts"),
        sa.UniqueConstraint("email", name="uq_accounts_email"),
    )
    op.create_index("ix_accounts_role_status", "accounts", ["role", "approval_status"])
    op.create_index("ix_accounts_approval_status", "accounts", ["approval_status"])


def downgrade() -> None:
    op.drop_index("ix_accounts_approval_status", table_name="accounts")
    op.drop_index("ix_accounts_role_status", table_name="accounts")
    op.drop_table("accounts")
