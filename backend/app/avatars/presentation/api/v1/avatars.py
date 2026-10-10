from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import Account
from app.avatars.domain_service import AvatarDomainService
from app.avatars.repository import SQLAlchemyAvatarRepository
from app.avatars.schemas import (
    AvatarCreationResponse,
    AvatarDetailResponse,
    AvatarListItem,
    CreateAvatarRequest,
    JobStatusResponse,
    PatchAvatarRequest,
)
from app.child_profiles.models import ChildProfile
from app.presentation.api.middleware.auth import get_current_account
from app.presentation.api.middleware.child_profile import get_active_child_profile
from infrastructure.config import get_config
from infrastructure.database.session import get_session

router = APIRouter(prefix="/api/v1/avatars", tags=["avatars"])


def _service(session: AsyncSession) -> AvatarDomainService:
    cfg = get_config()
    return AvatarDomainService(SQLAlchemyAvatarRepository(session), cfg.REDIS_URL)


@router.post("", response_model=AvatarCreationResponse, status_code=201)
async def create_avatar(
    body: CreateAvatarRequest,
    request: Request,
    account: Account = Depends(get_current_account),
    child_profile: ChildProfile = Depends(get_active_child_profile),
    session: AsyncSession = Depends(get_session),
) -> AvatarCreationResponse:
    await request.app.state.rate_limiter.enforce(
        f"avatar:generation:{account.id}",
        limit=10,
        window_seconds=3600,
    )
    return await _service(session).create(account.id, body, child_profile.id)


@router.get("/{avatar_id}/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    avatar_id: uuid.UUID,
    job_id: uuid.UUID,
    account: Account = Depends(get_current_account),
    child_profile: ChildProfile = Depends(get_active_child_profile),
    session: AsyncSession = Depends(get_session),
) -> JobStatusResponse:
    return await _service(session).get_job(account.id, avatar_id, job_id, child_profile.id)


@router.get("", response_model=list[AvatarListItem])
async def list_avatars(
    account: Account = Depends(get_current_account),
    child_profile: ChildProfile = Depends(get_active_child_profile),
    session: AsyncSession = Depends(get_session),
) -> list[AvatarListItem]:
    return await _service(session).list(account.id, child_profile.id)


@router.get("/{avatar_id}", response_model=AvatarDetailResponse)
async def get_avatar(
    avatar_id: uuid.UUID,
    account: Account = Depends(get_current_account),
    child_profile: ChildProfile = Depends(get_active_child_profile),
    session: AsyncSession = Depends(get_session),
) -> AvatarDetailResponse:
    return await _service(session).get(account.id, avatar_id, child_profile.id)


@router.patch("/{avatar_id}", response_model=AvatarDetailResponse)
async def patch_avatar(
    avatar_id: uuid.UUID,
    body: PatchAvatarRequest,
    account: Account = Depends(get_current_account),
    child_profile: ChildProfile = Depends(get_active_child_profile),
    session: AsyncSession = Depends(get_session),
) -> AvatarDetailResponse:
    return await _service(session).update(account.id, avatar_id, body, child_profile.id)


@router.post("/{avatar_id}/regenerate", response_model=AvatarCreationResponse, status_code=201)
async def regenerate_avatar(
    avatar_id: uuid.UUID,
    request: Request,
    account: Account = Depends(get_current_account),
    child_profile: ChildProfile = Depends(get_active_child_profile),
    session: AsyncSession = Depends(get_session),
) -> AvatarCreationResponse:
    await request.app.state.rate_limiter.enforce(
        f"avatar:generation:{account.id}",
        limit=10,
        window_seconds=3600,
    )
    return await _service(session).regenerate(account.id, avatar_id, child_profile.id)


@router.delete("/{avatar_id}", status_code=204, response_model=None)
async def delete_avatar(
    avatar_id: uuid.UUID,
    account: Account = Depends(get_current_account),
    child_profile: ChildProfile = Depends(get_active_child_profile),
    session: AsyncSession = Depends(get_session),
) -> None:
    await _service(session).delete(account.id, avatar_id, child_profile.id)
