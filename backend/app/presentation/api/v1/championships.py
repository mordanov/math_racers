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
from app.presentation.api.middleware.auth import get_current_account
from infrastructure.database.session import get_session

router = APIRouter(prefix="/api/v1/championships", tags=["championships"])


def _service(session: AsyncSession) -> ChampionshipDomainService:
    return ChampionshipDomainService(SQLAlchemyChampionshipRepository(session))


@router.post("", response_model=ChampionshipResponse, status_code=201)
async def create_championship(
    body: CreateChampionshipRequest,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> ChampionshipResponse:
    return await _service(session).create(account.id, body)


@router.get("/{championship_id}", response_model=ChampionshipResponse)
async def get_championship(
    championship_id: uuid.UUID,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> ChampionshipResponse:
    return await _service(session).get(account.id, championship_id)


@router.patch("/{championship_id}/races/{race_id}", response_model=ChampionshipResponse)
async def record_championship_race(
    championship_id: uuid.UUID,
    race_id: uuid.UUID,
    body: RecordRaceRequest,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> ChampionshipResponse:
    return await _service(session).record_race(
        account.id, championship_id, race_id, body
    )
