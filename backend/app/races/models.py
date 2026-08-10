from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
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
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seed: Mapped[str] = mapped_column(String, nullable=False)
    difficulty_tier: Mapped[int] = mapped_column(Integer, nullable=False)
    mode: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    participants: Mapped[list[RaceParticipant]] = relationship(
        "RaceParticipant", back_populates="race", cascade="all, delete-orphan"
    )


class RaceParticipant(Base):
    __tablename__ = "race_participants"
    __table_args__ = (
        CheckConstraint("position BETWEEN 1 AND 5", name="ck_race_participants_position"),
        CheckConstraint(
            "problems_correct BETWEEN 0 AND 8", name="ck_race_participants_problems_correct"
        ),
        CheckConstraint(
            "total_distance BETWEEN 0 AND 144", name="ck_race_participants_total_distance"
        ),
        CheckConstraint("xp_earned >= 0", name="ck_race_participants_xp_earned"),
        CheckConstraint(
            "average_response_ms >= 0", name="ck_race_participants_average_response_ms"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    race_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("races.id", ondelete="CASCADE"),
        nullable=False,
    )
    avatar_id: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    problems_correct: Mapped[int] = mapped_column(Integer, nullable=False)
    average_response_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    total_distance: Mapped[int] = mapped_column(Integer, nullable=False)
    xp_earned: Mapped[int] = mapped_column(Integer, nullable=False)

    race: Mapped[Race] = relationship("Race", back_populates="participants")
