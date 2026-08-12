"""game modes: nullable position, championships tables

Revision ID: 0006
Revises: 0005
Create Date: 2026-08-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make race_participants.position nullable and replace constraint
    op.drop_constraint("ck_race_participants_position", "race_participants")
    op.alter_column("race_participants", "position", nullable=True)
    op.create_check_constraint(
        "ck_race_participants_position",
        "race_participants",
        "position IS NULL OR position BETWEEN 1 AND 5",
    )

    op.create_table(
        "championships",
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
        sa.Column("total_races", sa.Integer(), nullable=False),
        sa.Column("races_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "total_races BETWEEN 3 AND 7", name="ck_championships_total_races"
        ),
        sa.CheckConstraint(
            "status IN ('active', 'completed')", name="ck_championships_status"
        ),
    )

    op.create_table(
        "championship_races",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "championship_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("championships.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "race_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("races.id"),
            nullable=False,
        ),
        sa.Column("race_index", sa.Integer(), nullable=False),
        sa.Column("avatar_id", sa.String(), nullable=False),
        sa.Column("is_player", sa.Boolean(), nullable=False),
        sa.Column("finishing_position", sa.Integer(), nullable=False),
        sa.Column("points_earned", sa.Integer(), nullable=False),
        sa.UniqueConstraint(
            "race_id", "avatar_id", name="uq_championship_races_race_avatar"
        ),
        sa.CheckConstraint(
            "finishing_position BETWEEN 1 AND 5",
            name="ck_championship_races_finishing_position",
        ),
        sa.CheckConstraint(
            "points_earned BETWEEN 0 AND 10", name="ck_championship_races_points_earned"
        ),
    )

    op.create_index(
        "ix_championship_races_championship_id",
        "championship_races",
        ["championship_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_championship_races_championship_id", table_name="championship_races"
    )
    op.drop_table("championship_races")
    op.drop_table("championships")

    op.drop_constraint("ck_race_participants_position", "race_participants")
    op.alter_column("race_participants", "position", nullable=False)
    op.create_check_constraint(
        "ck_race_participants_position",
        "race_participants",
        "position BETWEEN 1 AND 5",
    )
