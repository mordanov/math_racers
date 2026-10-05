from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import Account
from app.child_profiles.repository import SQLAlchemyChildProfileRepository
from app.child_profiles.schemas import (
    ChildProfileListResponse,
    ChildProfileResponse,
    CreateChildProfileRequest,
)
from app.presentation.api.middleware.auth import get_current_account
from app.shared.exceptions import ConflictError, NotFoundError, PermissionError
from infrastructure.database.session import get_session

_MAX_PROFILES = 5

router = APIRouter(tags=["child-profiles"])


@router.get("/api/v1/child-profiles", response_model=ChildProfileListResponse)
async def list_child_profiles(
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> ChildProfileListResponse:
    repo = SQLAlchemyChildProfileRepository(session)
    profiles = await repo.list_for_account(account.id)
    return ChildProfileListResponse(
        profiles=[ChildProfileResponse.model_validate(p) for p in profiles]
    )


@router.post(
    "/api/v1/child-profiles",
    response_model=ChildProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_child_profile(
    body: CreateChildProfileRequest,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> ChildProfileResponse:
    repo = SQLAlchemyChildProfileRepository(session)
    count = await repo.count_for_account(account.id)
    if count >= _MAX_PROFILES:
        raise ConflictError(
            "MAX_CHILD_PROFILES",
            f"Maximum of {_MAX_PROFILES} child profiles reached.",
        )
    profile = await repo.create(account.id, body.display_name)
    return ChildProfileResponse.model_validate(profile)


@router.delete("/api/v1/child-profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_child_profile(
    profile_id: uuid.UUID,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> None:
    repo = SQLAlchemyChildProfileRepository(session)
    profile = await repo.get(profile_id)
    if profile is None:
        raise NotFoundError("CHILD_PROFILE_NOT_FOUND", "Child profile not found.")
    if profile.account_id != account.id:
        raise PermissionError("FORBIDDEN", "Not your child profile.")
    await repo.delete(profile_id)
