from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import Account
from app.child_profiles.repository import SQLAlchemyChildProfileRepository
from app.child_profiles.schemas import (
    ChildProfileListResponse,
    ChildProfileResponse,
    CreateChildProfileRequest,
    LegacyDataAssignmentRequest,
)
from app.presentation.api.middleware.auth import get_current_account
from application.assign_legacy_child_data import AssignLegacyChildDataUseCase
from application.export_child_data import ExportChildDataUseCase
from application.manage_child_profiles import ManageChildProfilesUseCase
from infrastructure.database.session import get_session

router = APIRouter(tags=["child-profiles"])


@router.get("/api/v1/child-profiles", response_model=ChildProfileListResponse)
async def list_child_profiles(
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> ChildProfileListResponse:
    profiles = await ManageChildProfilesUseCase(
        SQLAlchemyChildProfileRepository(session)
    ).list_for_account(account.id)
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
    profile = await ManageChildProfilesUseCase(SQLAlchemyChildProfileRepository(session)).create(
        account.id, body.display_name
    )
    return ChildProfileResponse.model_validate(profile)


@router.delete(
    "/api/v1/child-profiles/{profile_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
)
async def delete_child_profile(
    profile_id: uuid.UUID,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> None:
    await ManageChildProfilesUseCase(SQLAlchemyChildProfileRepository(session)).delete(
        account.id, profile_id
    )


@router.get("/api/v1/child-profiles/{profile_id}/legacy-data")
async def list_unassigned_legacy_data(
    profile_id: uuid.UUID,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    await ManageChildProfilesUseCase(SQLAlchemyChildProfileRepository(session)).get_owned(
        account.id, profile_id
    )
    records = await AssignLegacyChildDataUseCase(session).list_unassigned(account.id)
    return {"records": records}


@router.post("/api/v1/child-profiles/{profile_id}/legacy-data/assign")
async def assign_legacy_data(
    profile_id: uuid.UUID,
    body: LegacyDataAssignmentRequest,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> dict[str, int]:
    await ManageChildProfilesUseCase(SQLAlchemyChildProfileRepository(session)).get_owned(
        account.id, profile_id
    )
    assigned = await AssignLegacyChildDataUseCase(session).execute(
        account.id, profile_id, body.records
    )
    return {"assigned": assigned}


@router.get("/api/v1/child-profiles/{profile_id}/export")
async def export_child_data(
    profile_id: uuid.UUID,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> JSONResponse:
    await ManageChildProfilesUseCase(SQLAlchemyChildProfileRepository(session)).get_owned(
        account.id, profile_id
    )
    data = await ExportChildDataUseCase(session).execute(account.id, profile_id)
    return JSONResponse(content=data)
