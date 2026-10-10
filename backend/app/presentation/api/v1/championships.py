from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import Account
from app.championships.domain_service import ChampionshipDomainService
from app.championships.repository import SQLAlchemyChampionshipRepository
from app.championships.schemas import (
    ChampionshipResponse,
    CreateChampionshipRequest,
    RecordRaceRequest,
)
from app.child_profiles.models import ChildProfile
from app.presentation.api.middleware.auth import get_current_account
from app.presentation.api.middleware.child_profile import get_active_child_profile
from app.progression.repository import SQLAlchemyProgressionRepository
from infrastructure.database.session import get_session

router = APIRouter(prefix="/api/v1/championships", tags=["championships"])


def _service(session: AsyncSession) -> ChampionshipDomainService:
    return ChampionshipDomainService(
        SQLAlchemyChampionshipRepository(session),
        SQLAlchemyProgressionRepository(session),
    )


@router.post("", response_model=ChampionshipResponse, status_code=201)
async def create_championship(
    body: CreateChampionshipRequest,
    account: Account = Depends(get_current_account),
    child_profile: ChildProfile = Depends(get_active_child_profile),
    session: AsyncSession = Depends(get_session),
) -> ChampionshipResponse:
    return await _service(session).create(account.id, body, child_profile.id)


@router.get("/{championship_id}", response_model=ChampionshipResponse)
async def get_championship(
    championship_id: uuid.UUID,
    account: Account = Depends(get_current_account),
    child_profile: ChildProfile = Depends(get_active_child_profile),
    session: AsyncSession = Depends(get_session),
) -> ChampionshipResponse:
    return await _service(session).get(account.id, championship_id, child_profile.id)


@router.patch("/{championship_id}/races/{race_id}", response_model=ChampionshipResponse)
async def record_championship_race(
    championship_id: uuid.UUID,
    race_id: uuid.UUID,
    body: RecordRaceRequest,
    account: Account = Depends(get_current_account),
    child_profile: ChildProfile = Depends(get_active_child_profile),
    session: AsyncSession = Depends(get_session),
) -> ChampionshipResponse:
    return await _service(session).record_race(
        account.id, championship_id, race_id, body, child_profile.id
    )
