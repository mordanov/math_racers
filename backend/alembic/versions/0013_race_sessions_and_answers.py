"""separate race setup and result data

Revision ID: 0013
Revises: 0012
Create Date: 2026-10-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0013"
down_revision: str | None = "0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "avatar_stats",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
    )
    op.add_column(
        "avatar_stats",
        sa.Column(
            "child_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("child_profiles.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.drop_constraint("avatar_stats_pkey", "avatar_stats", type_="primary")
    op.create_primary_key("avatar_stats_pkey", "avatar_stats", ["id"])
    op.create_index(
        "uq_avatar_stats_avatar_child",
        "avatar_stats",
        ["avatar_id", "child_profile_id"],
        unique=True,
    )
    op.add_column(
        "championships",
        sa.Column(
            "child_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("child_profiles.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.create_index("idx_championships_child_profile_id", "championships", ["child_profile_id"])
    op.create_unique_constraint(
        "uq_championship_races_championship_index",
        "championship_races",
        ["championship_id", "race_index"],
    )
    op.create_unique_constraint(
        "uq_championship_races_championship_race",
        "championship_races",
        ["championship_id", "race_id"],
    )
    op.add_column(
        "xp_events",
        sa.Column(
            "championship_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("championships.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.create_index(
        "uq_xp_events_championship_bonus",
        "xp_events",
        ["championship_id"],
        unique=True,
        postgresql_where=sa.text("source = 'championship_bonus' AND championship_id IS NOT NULL"),
    )
    op.add_column(
        "avatars",
        sa.Column(
            "child_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("child_profiles.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.create_index("idx_avatars_child_profile_id", "avatars", ["child_profile_id"])
    op.add_column(
        "player_achievements",
        sa.Column(
            "child_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("child_profiles.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.drop_constraint("uq_player_achievements", "player_achievements", type_="unique")
    op.create_unique_constraint(
        "uq_player_achievements_child_key",
        "player_achievements",
        ["account_id", "child_profile_id", "achievement_key"],
    )
    op.create_table(
        "child_progressions",
        sa.Column(
            "child_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("child_profiles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("total_xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("total_xp >= 0", name="ck_child_progressions_total_xp"),
        sa.CheckConstraint("current_level >= 1", name="ck_child_progressions_current_level"),
    )
    op.add_column(
        "xp_events",
        sa.Column(
            "child_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("child_profiles.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.create_index("idx_xp_events_child_profile_id", "xp_events", ["child_profile_id"])
    op.add_column(
        "race_sessions",
        sa.Column(
            "child_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("child_profiles.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.create_index(
        "idx_race_sessions_child_profile_id",
        "race_sessions",
        ["child_profile_id"],
    )
    op.drop_constraint("ck_race_participants_problems_correct", "race_participants", type_="check")
    op.create_check_constraint(
        "ck_race_participants_problems_correct",
        "race_participants",
        "problems_correct >= 0",
    )
    op.drop_constraint("ck_race_participants_total_distance", "race_participants", type_="check")
    op.create_check_constraint(
        "ck_race_participants_total_distance",
        "race_participants",
        "total_distance >= 0",
    )
    op.add_column(
        "races",
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.execute(sa.text("""
            UPDATE races AS race
            SET account_id = race_session.account_id
            FROM race_sessions AS race_session
            WHERE race.id = race_session.race_id
              AND race.account_id IS NULL
        """))
    op.execute(sa.text("""
            UPDATE races AS race
            SET account_id = championship.account_id
            FROM championship_races AS championship_race
            JOIN championships AS championship
              ON championship.id = championship_race.championship_id
            WHERE race.id = championship_race.race_id
              AND race.account_id IS NULL
        """))
    op.add_column(
        "races",
        sa.Column(
            "child_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("child_profiles.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.add_column("races", sa.Column("avatar_id", sa.String(), nullable=True))
    op.add_column("races", sa.Column("opponent_count", sa.Integer(), nullable=True))
    op.add_column(
        "races",
        sa.Column("custom_tier_config", postgresql.JSONB(), nullable=True),
    )
    op.add_column(
        "races",
        sa.Column(
            "championship_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("championships.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "races",
        sa.Column("status", sa.String(), nullable=False, server_default="completed"),
    )
    op.add_column(
        "races",
        sa.Column("idempotency_key", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column("races", sa.Column("result_payload", postgresql.JSONB(), nullable=True))
    op.add_column("races", sa.Column("result_response", postgresql.JSONB(), nullable=True))
    op.create_check_constraint(
        "ck_races_status",
        "races",
        "status IN ('active', 'completed', 'abandoned')",
    )
    op.create_index("idx_races_child_profile_id", "races", ["child_profile_id"])
    op.create_index(
        "uq_races_idempotency_key",
        "races",
        ["idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )
    op.create_table(
        "race_answers",
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
        sa.Column("operation", sa.String(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("response_time_ms", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "operation IN ('addition', 'subtraction', 'multiplication', 'division')",
            name="ck_race_answers_operation",
        ),
        sa.CheckConstraint("response_time_ms >= 0", name="ck_race_answers_response_time"),
    )
    op.create_index("idx_race_answers_race_id", "race_answers", ["race_id"])


def downgrade() -> None:
    op.drop_index("uq_avatar_stats_avatar_child", table_name="avatar_stats")
    op.drop_constraint("avatar_stats_pkey", "avatar_stats", type_="primary")
    op.create_primary_key("avatar_stats_pkey", "avatar_stats", ["avatar_id"])
    op.drop_column("avatar_stats", "child_profile_id")
    op.drop_column("avatar_stats", "id")
    op.drop_index("uq_xp_events_championship_bonus", table_name="xp_events")
    op.drop_column("xp_events", "championship_id")
    op.drop_constraint(
        "uq_championship_races_championship_race", "championship_races", type_="unique"
    )
    op.drop_constraint(
        "uq_championship_races_championship_index", "championship_races", type_="unique"
    )
    op.drop_index("idx_championships_child_profile_id", table_name="championships")
    op.drop_column("championships", "child_profile_id")
    op.drop_constraint("uq_player_achievements_child_key", "player_achievements", type_="unique")
    op.create_unique_constraint(
        "uq_player_achievements", "player_achievements", ["account_id", "achievement_key"]
    )
    op.drop_column("player_achievements", "child_profile_id")
    op.drop_index("idx_avatars_child_profile_id", table_name="avatars")
    op.drop_column("avatars", "child_profile_id")
    op.drop_index("idx_xp_events_child_profile_id", table_name="xp_events")
    op.drop_column("xp_events", "child_profile_id")
    op.drop_table("child_progressions")
    op.drop_index("idx_race_sessions_child_profile_id", table_name="race_sessions")
    op.drop_column("race_sessions", "child_profile_id")
    op.drop_index("idx_race_answers_race_id", table_name="race_answers")
    op.drop_table("race_answers")
    op.drop_index("uq_races_idempotency_key", table_name="races")
    op.drop_index("idx_races_child_profile_id", table_name="races")
    op.drop_constraint("ck_races_status", "races", type_="check")
    op.drop_column("races", "result_response")
    op.drop_column("races", "result_payload")
    op.drop_column("races", "idempotency_key")
    op.drop_column("races", "status")
    op.drop_column("races", "championship_id")
    op.drop_column("races", "custom_tier_config")
    op.drop_column("races", "opponent_count")
    op.drop_column("races", "avatar_id")
    op.drop_column("races", "child_profile_id")
    op.drop_column("races", "account_id")
    op.drop_constraint("ck_race_participants_problems_correct", "race_participants", type_="check")
    op.create_check_constraint(
        "ck_race_participants_problems_correct",
        "race_participants",
        "problems_correct BETWEEN 0 AND 8",
    )
    op.drop_constraint("ck_race_participants_total_distance", "race_participants", type_="check")
    op.create_check_constraint(
        "ck_race_participants_total_distance",
        "race_participants",
        "total_distance BETWEEN 0 AND 144",
    )
