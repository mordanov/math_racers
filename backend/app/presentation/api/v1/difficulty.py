from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.mathematics.difficulty import select_tier
from app.mathematics.exceptions import PlayerNotFoundError
from app.mathematics.models import PlayerDifficulty
from app.mathematics.repository import SQLAlchemyPlayerDifficultyRepository
from app.mathematics.schemas import DifficultyPatchRequest, DifficultyResponse
from app.presentation.api.middleware.auth import (
    get_current_account,
    require_administrator,
)
from app.accounts.models import Account
from infrastructure.database.session import get_session

router = APIRouter(prefix="/api/v1/players", tags=["mathematics"])


@router.get("/{player_id}/difficulty", response_model=DifficultyResponse)
async def get_difficulty(
    player_id: uuid.UUID,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> DifficultyResponse:
    repo = SQLAlchemyPlayerDifficultyRepository(session)
    record = await repo.get_by_player_id(player_id)
    if record is None:
        raise PlayerNotFoundError(player_id)
    effective = select_tier(record.current_tier, 0.75, record.parent_override)
    return DifficultyResponse(
        player_id=record.player_id,
        current_tier=record.current_tier,
        parent_override=record.parent_override,
        effective_tier=effective,
    )


@router.patch("/{player_id}/difficulty", response_model=DifficultyResponse)
async def patch_difficulty(
    player_id: uuid.UUID,
    body: DifficultyPatchRequest,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> DifficultyResponse:
    repo = SQLAlchemyPlayerDifficultyRepository(session)
    record = await repo.get_by_player_id(player_id)
    if record is None:
        raise PlayerNotFoundError(player_id)

    updated = PlayerDifficulty(
        player_id=record.player_id,
        current_tier=record.current_tier,
        parent_override=body.parent_override,
    )
    saved = await repo.upsert(updated)
    effective = select_tier(saved.current_tier, 0.75, saved.parent_override)
    return DifficultyResponse(
        player_id=saved.player_id,
        current_tier=saved.current_tier,
        parent_override=saved.parent_override,
        effective_tier=effective,
    )
