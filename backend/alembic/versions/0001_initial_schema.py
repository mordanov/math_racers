"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "job_audit",
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column("job_type", sa.String(length=100), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
    )
    op.create_index("ix_job_audit_status", "job_audit", ["status"])
    op.create_index("ix_job_audit_created_at", "job_audit", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_job_audit_created_at", table_name="job_audit")
    op.drop_index("ix_job_audit_status", table_name="job_audit")
    op.drop_table("job_audit")
