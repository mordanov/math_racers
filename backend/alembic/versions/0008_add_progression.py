"""player_progressions, xp_events tables; longest_streak column on race_participants

Revision ID: 0008
Revises: 0007
Create Date: 2026-08-12
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "race_participants",
        sa.Column(
            "longest_streak",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.create_check_constraint(
        "ck_race_participants_longest_streak",
        "race_participants",
        "longest_streak >= 0",
    )

    op.create_table(
        "player_progressions",
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("total_xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_level", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("total_xp >= 0", name="ck_player_progressions_total_xp"),
        sa.CheckConstraint(
            "current_level >= 0", name="ck_player_progressions_current_level"
        ),
    )

    op.create_table(
        "xp_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column(
            "race_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("races.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "source IN ('race_completion','correct_answer','streak_bonus','championship_bonus')",
            name="ck_xp_events_source",
        ),
        sa.CheckConstraint("amount > 0", name="ck_xp_events_amount"),
    )
    op.create_index("idx_xp_events_account_id", "xp_events", ["account_id"])
    op.create_index("idx_xp_events_race_id", "xp_events", ["race_id"])


def downgrade() -> None:
    op.drop_index("idx_xp_events_race_id", table_name="xp_events")
    op.drop_index("idx_xp_events_account_id", table_name="xp_events")
    op.drop_table("xp_events")
    op.drop_table("player_progressions")
    op.drop_constraint(
        "ck_race_participants_longest_streak", "race_participants", type_="check"
    )
    op.drop_column("race_participants", "longest_streak")
