from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base


class PlayerStats(Base):
    __tablename__ = "player_stats"
    __table_args__ = (
        CheckConstraint("total_races >= 0", name="ck_player_stats_total_races"),
        CheckConstraint("correct_answers >= 0", name="ck_player_stats_correct_answers"),
        CheckConstraint("best_streak >= 0", name="ck_player_stats_best_streak"),
    )

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    total_races: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_problems_solved: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    correct_answers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_response_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    best_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class AvatarStats(Base):
    __tablename__ = "avatar_stats"
    __table_args__ = (
        CheckConstraint("total_races >= 0", name="ck_avatar_stats_total_races"),
        Index("idx_avatar_stats_account_id", "account_id"),
    )

    # No FK — avatar_id is plain UUID; records survive avatar deletion (spec Edge Case 2)
    avatar_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    total_races: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wins: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    podiums: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    best_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_race_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class RaceSession(Base):
    __tablename__ = "race_sessions"
    __table_args__ = (
        CheckConstraint(
            "mode IN ('quick', 'championship', 'duel', 'training')",
            name="ck_race_sessions_mode",
        ),
        CheckConstraint("problems_solved >= 0", name="ck_race_sessions_problems_solved"),
        CheckConstraint("correct_answers >= 0", name="ck_race_sessions_correct_answers"),
        Index("idx_race_sessions_account_id", "account_id"),
        Index("idx_race_sessions_finished_at", "finished_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    # No FK — avatar_id is plain UUID; records survive avatar deletion (spec Edge Case 2)
    avatar_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    race_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("races.id", ondelete="SET NULL"),
        nullable=True,
    )
    mode: Mapped[str] = mapped_column(String, nullable=False)
    finishing_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    problems_solved: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_answers: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty_tier: Mapped[int] = mapped_column(Integer, nullable=False)
    xp_earned: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_response_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    longest_streak: Mapped[int] = mapped_column(Integer, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
