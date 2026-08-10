from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.base import Base


class Avatar(Base):
    __tablename__ = "avatars"
    __table_args__ = (
        CheckConstraint(
            "species IN ('fox','rabbit','bear','cat','mouse','panda')",
            name="ck_avatars_species",
        ),
        CheckConstraint(
            "status IN ('pending','published','failed')",
            name="ck_avatars_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    species: Mapped[str] = mapped_column(String, nullable=False)
    fur_color: Mapped[str] = mapped_column(String(7), nullable=False)
    eye_color: Mapped[str] = mapped_column(String(7), nullable=False)
    hairstyle: Mapped[str] = mapped_column(String, nullable=False)
    accessories: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    clothes_top_color: Mapped[str] = mapped_column(String(7), nullable=False)
    clothes_bottom_color: Mapped[str] = mapped_column(String(7), nullable=False)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    personality: Mapped[str | None] = mapped_column(Text, nullable=True)
    biography: Mapped[str | None] = mapped_column(Text, nullable=True)
    appearance_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    favorite_subject: Mapped[str | None] = mapped_column(String, nullable=True)
    running_style: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    is_favourite: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    active_portrait_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("avatar_portraits.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    portraits: Mapped[list[AvatarPortrait]] = relationship(
        "AvatarPortrait",
        back_populates="avatar",
        cascade="all, delete-orphan",
        foreign_keys="AvatarPortrait.avatar_id",
        order_by="AvatarPortrait.version",
    )
    active_portrait: Mapped[AvatarPortrait | None] = relationship(
        "AvatarPortrait",
        foreign_keys=[active_portrait_id],
        lazy="joined",
    )
    generation_jobs: Mapped[list[GenerationJob]] = relationship(
        "GenerationJob",
        back_populates="avatar",
        cascade="all, delete-orphan",
    )


class AvatarPortrait(Base):
    __tablename__ = "avatar_portraits"
    __table_args__ = (
        UniqueConstraint("avatar_id", "version", name="uq_avatar_portraits_avatar_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    avatar_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("avatars.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt_version: Mapped[str] = mapped_column(String, nullable=False)
    model_version: Mapped[str] = mapped_column(String, nullable=False)
    full_url: Mapped[str] = mapped_column(String, nullable=False)
    medium_url: Mapped[str] = mapped_column(String, nullable=False)
    small_url: Mapped[str] = mapped_column(String, nullable=False)
    thumb_url: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    avatar: Mapped[Avatar] = relationship(
        "Avatar",
        back_populates="portraits",
        foreign_keys=[avatar_id],
    )
    jobs: Mapped[list[GenerationJob]] = relationship(
        "GenerationJob",
        back_populates="portrait",
    )


class GenerationJob(Base):
    __tablename__ = "generation_jobs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('queued','llm_running','prompt_building','generating','validating',"
            "'storing','complete','failed')",
            name="ck_generation_jobs_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    avatar_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("avatars.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    portrait_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("avatar_portraits.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String, nullable=False, default="queued")
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    prompt_version: Mapped[str | None] = mapped_column(String, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    avatar: Mapped[Avatar] = relationship("Avatar", back_populates="generation_jobs")
    portrait: Mapped[AvatarPortrait | None] = relationship(
        "AvatarPortrait", back_populates="jobs", foreign_keys=[portrait_id]
    )
