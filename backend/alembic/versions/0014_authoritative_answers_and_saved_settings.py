"""record server-timed answers and saved parent settings

Revision ID: 0014
Revises: 0013
Create Date: 2026-10-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0014"
down_revision: str | None = "0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "race_answers",
        sa.Column("answer_index", sa.Integer(), nullable=True),
    )
    op.add_column(
        "race_answers",
        sa.Column("problem_operand_a", sa.Integer(), nullable=True),
    )
    op.add_column(
        "race_answers",
        sa.Column("problem_operand_b", sa.Integer(), nullable=True),
    )
    op.add_column(
        "race_answers",
        sa.Column("submitted_answer", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "race_answers",
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "uq_race_answers_race_index",
        "race_answers",
        ["race_id", "answer_index"],
        unique=True,
        postgresql_where=sa.text("answer_index IS NOT NULL"),
    )
    op.add_column(
        "player_progressions",
        sa.Column(
            "assigned_child_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("child_profiles.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(
        "idx_player_progressions_assigned_child",
        "player_progressions",
        ["assigned_child_profile_id"],
    )
    op.add_column(
        "player_difficulty",
        sa.Column("custom_tier_config", postgresql.JSONB(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("player_difficulty", "custom_tier_config")
    op.drop_index("idx_player_progressions_assigned_child", table_name="player_progressions")
    op.drop_column("player_progressions", "assigned_child_profile_id")
    op.drop_index("uq_race_answers_race_index", table_name="race_answers")
    op.drop_column("race_answers", "answered_at")
    op.drop_column("race_answers", "submitted_answer")
    op.drop_column("race_answers", "problem_operand_b")
    op.drop_column("race_answers", "problem_operand_a")
    op.drop_column("race_answers", "answer_index")
