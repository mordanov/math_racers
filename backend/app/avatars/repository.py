from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.avatars.models import Avatar, AvatarPortrait, GenerationJob
from app.shared.exceptions import NotFoundError

_TERMINAL_STATUSES = ("complete", "failed")


class AvatarRepository(Protocol):
    async def create(self, account_id: uuid.UUID, fields: dict[str, Any]) -> Avatar: ...
    async def get(self, avatar_id: uuid.UUID) -> Avatar: ...
    async def list_by_account(self, account_id: uuid.UUID) -> list[Avatar]: ...
    async def update(self, avatar: Avatar) -> Avatar: ...
    async def delete(self, avatar: Avatar) -> None: ...
    async def count_by_account(self, account_id: uuid.UUID) -> int: ...

    async def create_portrait(self, fields: dict[str, Any]) -> AvatarPortrait: ...
    async def get_portrait(self, portrait_id: uuid.UUID) -> AvatarPortrait | None: ...
    async def list_portraits(self, avatar_id: uuid.UUID) -> list[AvatarPortrait]: ...
    async def next_portrait_version(self, avatar_id: uuid.UUID) -> int: ...

    async def create_job(self, avatar_id: uuid.UUID) -> GenerationJob: ...
    async def get_job(self, job_id: uuid.UUID) -> GenerationJob | None: ...
    async def update_job(self, job: GenerationJob) -> GenerationJob: ...
    async def count_active_jobs_by_account(self, account_id: uuid.UUID) -> int: ...
    async def count_jobs_last_hour_by_account(self, account_id: uuid.UUID) -> int: ...


class SQLAlchemyAvatarRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Avatar ────────────────────────────────────────────────────────────────

    async def create(self, account_id: uuid.UUID, fields: dict[str, Any]) -> Avatar:
        avatar = Avatar(account_id=account_id, **fields)
        self._session.add(avatar)
        await self._session.flush()
        return await self.get(avatar.id)

    async def get(self, avatar_id: uuid.UUID) -> Avatar:
        result = await self._session.execute(
            select(Avatar)
            .where(Avatar.id == avatar_id)
            .options(
                selectinload(Avatar.portraits),
                selectinload(Avatar.active_portrait),
                selectinload(Avatar.generation_jobs),
            )
        )
        avatar = result.scalar_one_or_none()
        if avatar is None:
            raise NotFoundError(
                error_code="AVATAR_NOT_FOUND",
                message=f"Avatar {avatar_id} not found.",
            )
        return avatar

    async def list_by_account(self, account_id: uuid.UUID) -> list[Avatar]:
        result = await self._session.execute(
            select(Avatar)
            .where(Avatar.account_id == account_id)
            .options(selectinload(Avatar.active_portrait))
            .order_by(Avatar.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, avatar: Avatar) -> Avatar:
        await self._session.flush()
        return avatar

    async def delete(self, avatar: Avatar) -> None:
        await self._session.delete(avatar)
        await self._session.flush()

    async def count_by_account(self, account_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(Avatar).where(Avatar.account_id == account_id)
        )
        return int(result.scalar_one())

    # ── AvatarPortrait ────────────────────────────────────────────────────────

    async def create_portrait(self, fields: dict[str, Any]) -> AvatarPortrait:
        portrait = AvatarPortrait(**fields)
        self._session.add(portrait)
        await self._session.flush()
        return portrait

    async def get_portrait(self, portrait_id: uuid.UUID) -> AvatarPortrait | None:
        result = await self._session.execute(
            select(AvatarPortrait).where(AvatarPortrait.id == portrait_id)
        )
        return result.scalar_one_or_none()

    async def list_portraits(self, avatar_id: uuid.UUID) -> list[AvatarPortrait]:
        result = await self._session.execute(
            select(AvatarPortrait)
            .where(AvatarPortrait.avatar_id == avatar_id)
            .order_by(AvatarPortrait.version)
        )
        return list(result.scalars().all())

    async def next_portrait_version(self, avatar_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.max(AvatarPortrait.version)).where(
                AvatarPortrait.avatar_id == avatar_id
            )
        )
        current_max = result.scalar_one_or_none()
        return (current_max or 0) + 1

    # ── GenerationJob ─────────────────────────────────────────────────────────

    async def create_job(self, avatar_id: uuid.UUID) -> GenerationJob:
        job = GenerationJob(avatar_id=avatar_id, status="queued", attempt=1)
        self._session.add(job)
        await self._session.flush()
        return job

    async def get_job(self, job_id: uuid.UUID) -> GenerationJob | None:
        result = await self._session.execute(
            select(GenerationJob).where(GenerationJob.id == job_id)
        )
        return result.scalar_one_or_none()

    async def update_job(self, job: GenerationJob) -> GenerationJob:
        await self._session.flush()
        return job

    async def count_active_jobs_by_account(self, account_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(GenerationJob)
            .join(Avatar, GenerationJob.avatar_id == Avatar.id)
            .where(
                Avatar.account_id == account_id,
                GenerationJob.status.notin_(_TERMINAL_STATUSES),
            )
        )
        return int(result.scalar_one())

    async def count_jobs_last_hour_by_account(self, account_id: uuid.UUID) -> int:
        cutoff = datetime.now(UTC) - timedelta(hours=1)
        result = await self._session.execute(
            select(func.count())
            .select_from(GenerationJob)
            .join(Avatar, GenerationJob.avatar_id == Avatar.id)
            .where(
                Avatar.account_id == account_id,
                GenerationJob.created_at >= cutoff,
            )
        )
        return int(result.scalar_one())
