from __future__ import annotations

import math
import uuid
from typing import TYPE_CHECKING

from infrastructure.logging import get_logger

if TYPE_CHECKING:
    from app.progression.repository import ProgressionRepository

from app.progression.schemas import LevelUpEvent, ProgressionResponse

logger = get_logger(__name__)


def _compute_level(total_xp: int) -> int:
    return max(1, math.floor(math.sqrt(total_xp / 100)))


def _xp_to_next_level(total_xp: int, current_level: int) -> int:
    return max(1, (current_level + 1) ** 2 * 100 - total_xp)


def _calculate_xp_delta(problems_correct: int, longest_streak: int, mode: str) -> int:
    correct_xp = problems_correct * 20
    if mode == "training":
        return correct_xp
    race_xp = 100
    streak_xp = math.floor(longest_streak / 5) * 10
    return race_xp + correct_xp + streak_xp


class ProgressionDomainService:
    def __init__(self, repository: ProgressionRepository) -> None:
        self._repository = repository

    async def award_xp(
        self,
        account_id: uuid.UUID,
        problems_correct: int,
        longest_streak: int,
        mode: str,
        race_id: uuid.UUID,
        child_profile_id: uuid.UUID | None = None,
    ) -> ProgressionResponse:
        xp_delta = _calculate_xp_delta(problems_correct, longest_streak, mode)

        if xp_delta > 0:
            new_total, new_level = await self._repository.add_xp(
                account_id, xp_delta, child_profile_id
            )
            old_level = _compute_level(new_total - xp_delta)
            await self._repository.insert_event(
                account_id, "race_completion", xp_delta, race_id, child_profile_id
            )
        else:
            existing = await self._repository.get(account_id, child_profile_id)
            new_total = existing.total_xp if existing is not None else 0
            new_level = existing.current_level if existing is not None else 1
            old_level = new_level

        level_up: LevelUpEvent | None = None
        if new_level > old_level:
            level_up = LevelUpEvent(
                previous_level=old_level,
                new_level=new_level,
                total_xp=new_total,
            )

        logger.info(
            "XP awarded",
            extra={
                "context": {
                    "account_id": str(account_id),
                    "xp_delta": xp_delta,
                    "new_total": new_total,
                    "new_level": new_level,
                    "level_up": level_up is not None,
                }
            },
        )

        return ProgressionResponse(
            total_xp=new_total,
            current_level=new_level,
            xp_to_next_level=_xp_to_next_level(new_total, new_level),
            xp_earned_this_race=xp_delta,
            level_up=level_up,
        )

    async def get_progression(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID | None = None
    ) -> ProgressionResponse:
        existing = await self._repository.get(account_id, child_profile_id)
        if existing is None:
            return ProgressionResponse(
                total_xp=0,
                current_level=1,
                xp_to_next_level=400,
            )
        return ProgressionResponse(
            total_xp=existing.total_xp,
            current_level=existing.current_level,
            xp_to_next_level=_xp_to_next_level(existing.total_xp, existing.current_level),
        )

    async def award_championship_completion(
        self,
        account_id: uuid.UUID,
        child_profile_id: uuid.UUID,
        championship_id: uuid.UUID,
    ) -> int:
        inserted = await self._repository.insert_championship_bonus_event(
            account_id, child_profile_id, championship_id
        )
        if not inserted:
            return 0

        await self._repository.add_xp(account_id, 500, child_profile_id)
        return 500
