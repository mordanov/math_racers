from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.base import Base


class Race(Base):
    __tablename__ = "races"
    __table_args__ = (
        CheckConstraint("difficulty_tier BETWEEN 1 AND 6", name="ck_races_difficulty_tier"),
        CheckConstraint(
            "mode IN ('quick', 'championship', 'duel', 'training')",
            name="ck_races_mode",
        ),
        CheckConstraint(
            "status IN ('active', 'completed', 'abandoned')",
            name="ck_races_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=True,
    )
    child_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("child_profiles.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    avatar_id: Mapped[str | None] = mapped_column(String, nullable=True)
    opponent_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    custom_tier_config: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)
    championship_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("championships.id", ondelete="SET NULL"),
        nullable=True,
    )
    seed: Mapped[str] = mapped_column(String, nullable=False)
    difficulty_tier: Mapped[int] = mapped_column(Integer, nullable=False)
    mode: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="completed")
    idempotency_key: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    result_payload: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)
    result_response: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    participants: Mapped[list[RaceParticipant]] = relationship(
        "RaceParticipant", back_populates="race", cascade="all, delete-orphan"
    )


class RaceAnswer(Base):
    __tablename__ = "race_answers"
    __table_args__ = (
        Index(
            "uq_race_answers_race_index",
            "race_id",
            "answer_index",
            unique=True,
            postgresql_where=text("answer_index IS NOT NULL"),
        ),
        CheckConstraint(
            "operation IN ('addition', 'subtraction', 'multiplication', 'division')",
            name="ck_race_answers_operation",
        ),
        CheckConstraint("response_time_ms >= 0", name="ck_race_answers_response_time"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    race_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("races.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    answer_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    problem_operand_a: Mapped[int | None] = mapped_column(Integer, nullable=True)
    problem_operand_b: Mapped[int | None] = mapped_column(Integer, nullable=True)
    operation: Mapped[str] = mapped_column(String, nullable=False)
    submitted_answer: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_correct: Mapped[bool] = mapped_column(nullable=False)
    response_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RaceParticipant(Base):
    __tablename__ = "race_participants"
    __table_args__ = (
        CheckConstraint(
            "position IS NULL OR position BETWEEN 1 AND 5",
            name="ck_race_participants_position",
        ),
        CheckConstraint(
            "problems_correct >= 0",
            name="ck_race_participants_problems_correct",
        ),
        CheckConstraint(
            "total_distance >= 0",
            name="ck_race_participants_total_distance",
        ),
        CheckConstraint("xp_earned >= 0", name="ck_race_participants_xp_earned"),
        CheckConstraint(
            "average_response_ms >= 0", name="ck_race_participants_average_response_ms"
        ),
        CheckConstraint("longest_streak >= 0", name="ck_race_participants_longest_streak"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    race_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("races.id", ondelete="CASCADE"),
        nullable=False,
    )
    avatar_id: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    problems_correct: Mapped[int] = mapped_column(Integer, nullable=False)
    average_response_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    total_distance: Mapped[int] = mapped_column(Integer, nullable=False)
    xp_earned: Mapped[int] = mapped_column(Integer, nullable=False)
    longest_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    race: Mapped[Race] = relationship("Race", back_populates="participants")
