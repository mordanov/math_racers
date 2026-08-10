from __future__ import annotations

from fastapi import APIRouter

from app.opponents.personalities import PERSONALITIES
from app.opponents.schemas import PersonalityDefinitionResponse

router = APIRouter(prefix="/api/v1", tags=["opponents"])


@router.get("/opponents/personalities", response_model=list[PersonalityDefinitionResponse])
async def get_personalities() -> list[PersonalityDefinitionResponse]:
    return PERSONALITIES
