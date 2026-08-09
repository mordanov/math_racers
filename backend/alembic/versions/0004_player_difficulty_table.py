"""player difficulty table

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-09
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "player_difficulty",
        sa.Column(
            "player_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("current_tier", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("parent_override", sa.Integer(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "current_tier BETWEEN 1 AND 6", name="ck_player_difficulty_current_tier"
        ),
        sa.CheckConstraint(
            "parent_override IS NULL OR parent_override BETWEEN 1 AND 6",
            name="ck_player_difficulty_parent_override",
        ),
    )


def downgrade() -> None:
    op.drop_table("player_difficulty")
