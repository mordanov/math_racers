from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.base import Base


class Championship(Base):
    __tablename__ = "championships"
    __table_args__ = (
        CheckConstraint("total_races BETWEEN 3 AND 7", name="ck_championships_total_races"),
        CheckConstraint("status IN ('active', 'completed')", name="ck_championships_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    total_races: Mapped[int] = mapped_column(Integer, nullable=False)
    races_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String, nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )

    championship_races: Mapped[list[ChampionshipRace]] = relationship(
        "ChampionshipRace", back_populates="championship", cascade="all, delete-orphan"
    )


class ChampionshipRace(Base):
    __tablename__ = "championship_races"
    __table_args__ = (
        CheckConstraint(
            "finishing_position BETWEEN 1 AND 5",
            name="ck_championship_races_finishing_position",
        ),
        CheckConstraint(
            "points_earned BETWEEN 0 AND 10", name="ck_championship_races_points_earned"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    championship_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("championships.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    race_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("races.id"),
        nullable=False,
    )
    race_index: Mapped[int] = mapped_column(Integer, nullable=False)
    avatar_id: Mapped[str] = mapped_column(String, nullable=False)
    is_player: Mapped[bool] = mapped_column(Boolean, nullable=False)
    finishing_position: Mapped[int] = mapped_column(Integer, nullable=False)
    points_earned: Mapped[int] = mapped_column(Integer, nullable=False)

    championship: Mapped[Championship] = relationship(
        "Championship", back_populates="championship_races"
    )
