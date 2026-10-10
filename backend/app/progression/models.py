from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base


class PlayerProgression(Base):
    __tablename__ = "player_progressions"
    __table_args__ = (
        CheckConstraint("total_xp >= 0", name="ck_player_progressions_total_xp"),
        CheckConstraint("current_level >= 0", name="ck_player_progressions_current_level"),
    )

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    assigned_child_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("child_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    total_xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class ChildProgression(Base):
    __tablename__ = "child_progressions"
    __table_args__ = (
        CheckConstraint("total_xp >= 0", name="ck_child_progressions_total_xp"),
        CheckConstraint("current_level >= 1", name="ck_child_progressions_current_level"),
    )

    child_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("child_profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    total_xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class XPEvent(Base):
    __tablename__ = "xp_events"
    __table_args__ = (
        CheckConstraint(
            "source IN ('race_completion','correct_answer','streak_bonus','championship_bonus')",
            name="ck_xp_events_source",
        ),
        CheckConstraint("amount > 0", name="ck_xp_events_amount"),
        Index("idx_xp_events_account_id", "account_id"),
        Index("idx_xp_events_race_id", "race_id"),
        Index(
            "uq_xp_events_championship_bonus",
            "championship_id",
            unique=True,
            postgresql_where=text("source = 'championship_bonus' AND championship_id IS NOT NULL"),
        ),
        Index("idx_xp_events_child_profile_id", "child_profile_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    child_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("child_profiles.id", ondelete="CASCADE"),
        nullable=True,
    )
    source: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    race_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("races.id", ondelete="SET NULL"),
        nullable=True,
    )
    championship_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("championships.id", ondelete="CASCADE"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
