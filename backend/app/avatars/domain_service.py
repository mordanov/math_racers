from __future__ import annotations

import json
import uuid
from typing import TYPE_CHECKING, Any

from app.avatars.schemas import (
    AvatarCreationResponse,
    AvatarDetailResponse,
    AvatarListItem,
    JobStatusResponse,
    PortraitSummary,
)
from app.shared.exceptions import NotFoundError, PermissionError, ValidationError

if TYPE_CHECKING:
    from app.avatars.models import Avatar, AvatarPortrait
    from app.avatars.repository import AvatarRepository
    from app.avatars.schemas import CreateAvatarRequest, PatchAvatarRequest

_MAX_AVATARS = 50
_MAX_CONCURRENT_JOBS = 2
_MAX_JOBS_PER_HOUR = 10


def _portrait_summary(portrait: AvatarPortrait | None) -> PortraitSummary | None:
    if portrait is None:
        return None
    return PortraitSummary(
        id=portrait.id,
        version=portrait.version,
        prompt_version=portrait.prompt_version,
        model_version=portrait.model_version,
        full_url=portrait.full_url,
        medium_url=portrait.medium_url,
        small_url=portrait.small_url,
        thumb_url=portrait.thumb_url,
        created_at=portrait.created_at,
    )


def _to_list_item(avatar: Avatar) -> AvatarListItem:
    return AvatarListItem(
        avatar_id=avatar.id,
        name=avatar.name,
        species=avatar.species,
        status=avatar.status,
        is_favourite=avatar.is_favourite,
        portrait=_portrait_summary(avatar.active_portrait),
        created_at=avatar.created_at,
    )


def _to_detail(avatar: Avatar) -> AvatarDetailResponse:
    return AvatarDetailResponse(
        avatar_id=avatar.id,
        species=avatar.species,
        fur_color=avatar.fur_color,
        eye_color=avatar.eye_color,
        hairstyle=avatar.hairstyle,
        accessories=list(avatar.accessories or []),
        clothes_top_color=avatar.clothes_top_color,
        clothes_bottom_color=avatar.clothes_bottom_color,
        name=avatar.name,
        personality=avatar.personality,
        biography=avatar.biography,
        appearance_summary=avatar.appearance_summary,
        favorite_subject=avatar.favorite_subject,
        running_style=avatar.running_style,
        status=avatar.status,
        is_favourite=avatar.is_favourite,
        active_portrait_id=avatar.active_portrait_id,
        portrait=_portrait_summary(avatar.active_portrait),
        portrait_history=[_portrait_summary(p) for p in avatar.portraits if p is not None],  # type: ignore[misc]
        created_at=avatar.created_at,
    )


def _enqueue_job(redis_url: str, job_id: uuid.UUID, avatar_id: uuid.UUID) -> None:
    import redis as _redis

    client = _redis.from_url(redis_url)
    payload = json.dumps(
        {"job_type": "avatar_generation", "job_id": str(job_id), "avatar_id": str(avatar_id)}
    )
    client.rpush("job_queue", payload)
    client.close()


class AvatarDomainService:
    def __init__(self, repository: AvatarRepository, redis_url: str) -> None:
        self._repository = repository
        self._redis_url = redis_url

    async def create(
        self, account_id: uuid.UUID, request: CreateAvatarRequest
    ) -> AvatarCreationResponse:
        count = await self._repository.count_by_account(account_id)
        if count >= _MAX_AVATARS:
            raise ValidationError(
                error_code="AVATAR_LIMIT_REACHED",
                message=f"Account may have at most {_MAX_AVATARS} avatars.",
            )

        active_jobs = await self._repository.count_active_jobs_by_account(account_id)
        if active_jobs >= _MAX_CONCURRENT_JOBS:
            raise ValidationError(
                error_code="CONCURRENCY_LIMIT_REACHED",
                message=f"At most {_MAX_CONCURRENT_JOBS} generation jobs may run at once.",
            )

        jobs_last_hour = await self._repository.count_jobs_last_hour_by_account(account_id)
        if jobs_last_hour >= _MAX_JOBS_PER_HOUR:
            raise ValidationError(
                error_code="RATE_LIMIT_EXCEEDED",
                message=f"At most {_MAX_JOBS_PER_HOUR} generation jobs per hour.",
            )

        avatar = await self._repository.create(
            account_id,
            {
                "species": request.species,
                "fur_color": request.fur_color,
                "eye_color": request.eye_color,
                "hairstyle": request.hairstyle,
                "accessories": request.accessories,
                "clothes_top_color": request.clothes_top_color,
                "clothes_bottom_color": request.clothes_bottom_color,
            },
        )

        job = await self._repository.create_job(avatar.id)
        _enqueue_job(self._redis_url, job.id, avatar.id)

        return AvatarCreationResponse(
            avatar_id=avatar.id,
            job_id=job.id,
            status="queued",
        )

    async def get_job(
        self, account_id: uuid.UUID, avatar_id: uuid.UUID, job_id: uuid.UUID
    ) -> JobStatusResponse:
        avatar = await self._repository.get(avatar_id)
        if avatar.account_id != account_id:
            raise PermissionError(
                error_code="AVATAR_ACCESS_DENIED",
                message="You do not own this avatar.",
            )
        job = await self._repository.get_job(job_id)
        if job is None or job.avatar_id != avatar_id:
            raise NotFoundError(
                error_code="JOB_NOT_FOUND",
                message=f"Job {job_id} not found.",
            )
        return JobStatusResponse(
            job_id=job.id,
            avatar_id=job.avatar_id,
            status=job.status,
            attempt=job.attempt,
            error=job.error,
            created_at=job.created_at,
            completed_at=job.completed_at,
        )

    async def get(self, account_id: uuid.UUID, avatar_id: uuid.UUID) -> AvatarDetailResponse:
        avatar = await self._repository.get(avatar_id)
        if avatar.account_id != account_id:
            raise PermissionError(
                error_code="AVATAR_ACCESS_DENIED",
                message="You do not own this avatar.",
            )
        return _to_detail(avatar)

    async def list(self, account_id: uuid.UUID) -> list[AvatarListItem]:
        avatars = await self._repository.list_by_account(account_id)
        return [_to_list_item(a) for a in avatars]

    async def regenerate(
        self, account_id: uuid.UUID, avatar_id: uuid.UUID
    ) -> AvatarCreationResponse:
        avatar = await self._repository.get(avatar_id)
        if avatar.account_id != account_id:
            raise PermissionError(
                error_code="AVATAR_ACCESS_DENIED",
                message="You do not own this avatar.",
            )

        active_jobs = await self._repository.count_active_jobs_by_account(account_id)
        if active_jobs >= _MAX_CONCURRENT_JOBS:
            raise ValidationError(
                error_code="CONCURRENCY_LIMIT_REACHED",
                message=f"At most {_MAX_CONCURRENT_JOBS} generation jobs may run at once.",
            )

        jobs_last_hour = await self._repository.count_jobs_last_hour_by_account(account_id)
        if jobs_last_hour >= _MAX_JOBS_PER_HOUR:
            raise ValidationError(
                error_code="RATE_LIMIT_EXCEEDED",
                message=f"At most {_MAX_JOBS_PER_HOUR} generation jobs per hour.",
            )

        job = await self._repository.create_job(avatar_id)
        _enqueue_job(self._redis_url, job.id, avatar_id)

        return AvatarCreationResponse(
            avatar_id=avatar_id,
            job_id=job.id,
            status="queued",
        )

    async def update(
        self, account_id: uuid.UUID, avatar_id: uuid.UUID, request: PatchAvatarRequest
    ) -> AvatarDetailResponse:
        avatar = await self._repository.get(avatar_id)
        if avatar.account_id != account_id:
            raise PermissionError(
                error_code="AVATAR_ACCESS_DENIED",
                message="You do not own this avatar.",
            )

        if request.name is not None:
            avatar.name = request.name
        if request.is_favourite is not None:
            avatar.is_favourite = request.is_favourite
        if request.active_portrait_id is not None:
            portrait = await self._repository.get_portrait(request.active_portrait_id)
            if portrait is None or portrait.avatar_id != avatar_id:
                raise NotFoundError(
                    error_code="PORTRAIT_NOT_FOUND",
                    message=f"Portrait {request.active_portrait_id} not found.",
                )
            avatar.active_portrait_id = request.active_portrait_id

        await self._repository.update(avatar)
        return _to_detail(avatar)

    async def delete(self, account_id: uuid.UUID, avatar_id: uuid.UUID) -> None:
        avatar = await self._repository.get(avatar_id)
        if avatar.account_id != account_id:
            raise PermissionError(
                error_code="AVATAR_ACCESS_DENIED",
                message="You do not own this avatar.",
            )
        await self._repository.delete(avatar)
