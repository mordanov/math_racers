from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import Account
from app.mathematics.difficulty import select_tier
from app.mathematics.exceptions import PlayerNotFoundError
from app.mathematics.models import PlayerDifficulty
from app.mathematics.repository import SQLAlchemyPlayerDifficultyRepository
from app.mathematics.schemas import (
    DifficultyPatchRequest,
    DifficultyResponse,
    Tier6SettingsPatchRequest,
    Tier6SettingsResponse,
)
from app.presentation.api.middleware.auth import (
    get_current_account,
)
from app.shared.exceptions import PermissionError
from infrastructure.database.session import get_session

router = APIRouter(prefix="/api/v1/players", tags=["mathematics"])


@router.get("/{player_id}/difficulty", response_model=DifficultyResponse)
async def get_difficulty(
    player_id: uuid.UUID,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> DifficultyResponse:
    if player_id != account.id:
        raise PermissionError("FORBIDDEN", "Difficulty settings belong to this parent account.")
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
    if player_id != account.id:
        raise PermissionError("FORBIDDEN", "Difficulty settings belong to this parent account.")
    repo = SQLAlchemyPlayerDifficultyRepository(session)
    record = await repo.get_by_player_id(player_id)
    current_tier = record.current_tier if record is not None else 1

    updated = PlayerDifficulty(
        player_id=player_id,
        current_tier=current_tier,
        parent_override=body.parent_override,
    )
    try:
        saved = await repo.upsert(updated)
    except Exception:
        raise PlayerNotFoundError(player_id) from None
    effective = select_tier(saved.current_tier, 0.75, saved.parent_override)
    return DifficultyResponse(
        player_id=saved.player_id,
        current_tier=saved.current_tier,
        parent_override=saved.parent_override,
        effective_tier=effective,
    )


@router.get("/{player_id}/tier-6-settings", response_model=Tier6SettingsResponse)
async def get_tier6_settings(
    player_id: uuid.UUID,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> Tier6SettingsResponse:
    if player_id != account.id:
        raise PermissionError("FORBIDDEN", "Tier 6 settings belong to this parent account.")
    record = await SQLAlchemyPlayerDifficultyRepository(session).get_by_player_id(player_id)
    return Tier6SettingsResponse(
        custom_tier_config=record.custom_tier_config if record is not None else None
    )


@router.patch("/{player_id}/tier-6-settings", response_model=Tier6SettingsResponse)
async def patch_tier6_settings(
    player_id: uuid.UUID,
    body: Tier6SettingsPatchRequest,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> Tier6SettingsResponse:
    if player_id != account.id:
        raise PermissionError("FORBIDDEN", "Tier 6 settings belong to this parent account.")
    repo = SQLAlchemyPlayerDifficultyRepository(session)
    record = await repo.get_by_player_id(player_id)
    if record is None:
        record = PlayerDifficulty(player_id=player_id)
    record.custom_tier_config = body.custom_tier_config.model_dump(mode="json")
    saved = await repo.upsert(record)
    return Tier6SettingsResponse(custom_tier_config=saved.custom_tier_config)
