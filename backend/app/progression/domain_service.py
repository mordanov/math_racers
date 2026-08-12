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
    return math.floor(math.sqrt(total_xp / 100))


def _xp_to_next_level(total_xp: int, current_level: int) -> int:
    return max(1, (current_level + 1) ** 2 * 100 - total_xp)


def _calculate_xp_delta(problems_correct: int, longest_streak: int, mode: str) -> int:
    race_xp = 100
    correct_xp = problems_correct * 20
    streak_xp = math.floor(longest_streak / 5) * 10
    mode_bonus = 500 if mode == "championship" else 0
    return race_xp + correct_xp + streak_xp + mode_bonus


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
    ) -> ProgressionResponse:
        xp_delta = _calculate_xp_delta(problems_correct, longest_streak, mode)

        existing = await self._repository.get(account_id)
        old_total = existing.total_xp if existing else 0
        old_level = _compute_level(old_total)

        new_total = old_total + xp_delta
        new_level = _compute_level(new_total)

        await self._repository.upsert(account_id, new_total, new_level)
        await self._repository.insert_event(
            account_id, "race_completion", xp_delta, race_id
        )

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

    async def get_progression(self, account_id: uuid.UUID) -> ProgressionResponse:
        existing = await self._repository.get(account_id)
        if existing is None:
            return ProgressionResponse(
                total_xp=0,
                current_level=0,
                xp_to_next_level=100,
            )
        return ProgressionResponse(
            total_xp=existing.total_xp,
            current_level=existing.current_level,
            xp_to_next_level=_xp_to_next_level(
                existing.total_xp, existing.current_level
            ),
        )
