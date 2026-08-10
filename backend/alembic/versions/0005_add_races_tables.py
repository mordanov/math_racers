"""add races tables

Revision ID: 0005
Revises: 0004
Create Date: 2026-08-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "races",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("seed", sa.String(), nullable=False),
        sa.Column("difficulty_tier", sa.Integer(), nullable=False),
        sa.Column("mode", sa.String(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("difficulty_tier BETWEEN 1 AND 6", name="ck_races_difficulty_tier"),
        sa.CheckConstraint(
            "mode IN ('quick', 'championship', 'duel', 'training')",
            name="ck_races_mode",
        ),
    )

    op.create_table(
        "race_participants",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "race_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("races.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("avatar_id", sa.String(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("problems_correct", sa.Integer(), nullable=False),
        sa.Column("average_response_ms", sa.Integer(), nullable=False),
        sa.Column("total_distance", sa.Integer(), nullable=False),
        sa.Column("xp_earned", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "position BETWEEN 1 AND 5", name="ck_race_participants_position"
        ),
        sa.CheckConstraint(
            "problems_correct BETWEEN 0 AND 8",
            name="ck_race_participants_problems_correct",
        ),
        sa.CheckConstraint(
            "total_distance BETWEEN 0 AND 144",
            name="ck_race_participants_total_distance",
        ),
        sa.CheckConstraint("xp_earned >= 0", name="ck_race_participants_xp_earned"),
        sa.CheckConstraint(
            "average_response_ms >= 0",
            name="ck_race_participants_average_response_ms",
        ),
    )


def downgrade() -> None:
    op.drop_table("race_participants")
    op.drop_table("races")
