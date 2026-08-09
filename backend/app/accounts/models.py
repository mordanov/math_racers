from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.base import Base


class AccountRole(StrEnum):
    parent = "parent"
    administrator = "administrator"


class ApprovalStatus(StrEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint("role IN ('parent', 'administrator')", name="ck_accounts_role"),
        CheckConstraint(
            "approval_status IN ('pending', 'approved', 'rejected')",
            name="ck_accounts_approval_status",
        ),
        Index("ix_accounts_role_status", "role", "approval_status"),
        Index("ix_accounts_approval_status", "approval_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(72), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default=AccountRole.parent)
    approval_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ApprovalStatus.pending
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,
    )

    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        "RefreshToken", back_populates="account", cascade="all, delete-orphan"
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        Index("ix_refresh_tokens_account_revoked", "account_id", "revoked_at"),
        Index("ix_refresh_tokens_expires_at", "expires_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    replaced_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("refresh_tokens.id", ondelete="SET NULL"),
        nullable=True,
    )

    account: Mapped[Account] = relationship("Account", back_populates="refresh_tokens")
