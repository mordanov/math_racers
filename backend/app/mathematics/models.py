from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base


class PlayerDifficulty(Base):
    __tablename__ = "player_difficulty"
    __table_args__ = (
        CheckConstraint("current_tier BETWEEN 1 AND 6", name="ck_player_difficulty_current_tier"),
        CheckConstraint(
            "parent_override IS NULL OR parent_override BETWEEN 1 AND 6",
            name="ck_player_difficulty_parent_override",
        ),
    )

    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    current_tier: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parent_override: Mapped[int | None] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=datetime.utcnow,
    )
