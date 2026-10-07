"""statistics tables

Revision ID: 0012
Revises: 0011
Create Date: 2026-10-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0012"
down_revision: str | None = "0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "player_stats",
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("total_races", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_problems_solved", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correct_answers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_response_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("best_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("total_races >= 0", name="ck_player_stats_total_races"),
        sa.CheckConstraint("correct_answers >= 0", name="ck_player_stats_correct_answers"),
        sa.CheckConstraint("best_streak >= 0", name="ck_player_stats_best_streak"),
    )

    op.create_table(
        "avatar_stats",
        sa.Column("avatar_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("total_races", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("podiums", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("best_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "last_race_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("total_races >= 0", name="ck_avatar_stats_total_races"),
    )
    op.create_index("idx_avatar_stats_account_id", "avatar_stats", ["account_id"])

    op.create_table(
        "race_sessions",
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
        sa.Column("avatar_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "race_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("races.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("mode", sa.String(), nullable=False),
        sa.Column("finishing_position", sa.Integer(), nullable=True),
        sa.Column("problems_solved", sa.Integer(), nullable=False),
        sa.Column("correct_answers", sa.Integer(), nullable=False),
        sa.Column("difficulty_tier", sa.Integer(), nullable=False),
        sa.Column("xp_earned", sa.Integer(), nullable=False),
        sa.Column("avg_response_ms", sa.Integer(), nullable=False),
        sa.Column("longest_streak", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "mode IN ('quick', 'championship', 'duel', 'training')",
            name="ck_race_sessions_mode",
        ),
        sa.CheckConstraint("problems_solved >= 0", name="ck_race_sessions_problems_solved"),
        sa.CheckConstraint("correct_answers >= 0", name="ck_race_sessions_correct_answers"),
    )
    op.create_index("idx_race_sessions_account_id", "race_sessions", ["account_id"])
    op.create_index("idx_race_sessions_finished_at", "race_sessions", ["finished_at"])


def downgrade() -> None:
    op.drop_index("idx_race_sessions_finished_at", table_name="race_sessions")
    op.drop_index("idx_race_sessions_account_id", table_name="race_sessions")
    op.drop_table("race_sessions")
    op.drop_index("idx_avatar_stats_account_id", table_name="avatar_stats")
    op.drop_table("avatar_stats")
    op.drop_table("player_stats")
