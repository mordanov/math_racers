from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from app.achievements.catalogue import CATALOGUE, get_by_key
from app.achievements.schemas import AchievementResponse
from infrastructure.logging import get_logger

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.achievements.repository import AchievementRepository

logger = get_logger(__name__)


# ── Predicate helpers ─────────────────────────────────────────────────────────


async def _count_races(account_id: uuid.UUID, session: AsyncSession) -> int:
    from sqlalchemy import text

    res = await session.execute(
        text("SELECT COUNT(*) FROM xp_events WHERE account_id = :aid"),
        {"aid": str(account_id)},
    )
    row = res.fetchone()
    return int(row[0]) if row else 0


# ── Predicate registry ────────────────────────────────────────────────────────

# Each predicate: async (account_id, event_data, session) -> bool
# event_data keys vary by trigger type (documented inline)


async def _pred_first_race(
    account_id: uuid.UUID, event_data: dict[str, Any], session: AsyncSession
) -> bool:
    race_count = await _count_races(account_id, session)
    return race_count >= 1


async def _pred_perfect_race(
    account_id: uuid.UUID, event_data: dict[str, Any], session: AsyncSession
) -> bool:
    return int(event_data.get("problems_correct", 0)) == 8


async def _pred_podium_finisher(
    account_id: uuid.UUID, event_data: dict[str, Any], session: AsyncSession
) -> bool:
    position = event_data.get("position")
    return position is not None and 1 <= position <= 3


async def _pred_champion(
    account_id: uuid.UUID, event_data: dict[str, Any], session: AsyncSession
) -> bool:
    return event_data.get("position") == 1


async def _pred_level_5(
    account_id: uuid.UUID, event_data: dict[str, Any], session: AsyncSession
) -> bool:
    return int(event_data.get("new_level", 0)) >= 5


async def _pred_level_10(
    account_id: uuid.UUID, event_data: dict[str, Any], session: AsyncSession
) -> bool:
    return int(event_data.get("new_level", 0)) >= 10


async def _pred_level_20(
    account_id: uuid.UUID, event_data: dict[str, Any], session: AsyncSession
) -> bool:
    return int(event_data.get("new_level", 0)) >= 20


# Keys evaluated per trigger type
_RACE_COMPLETED_KEYS = ["first_race", "perfect_race", "podium_finisher", "champion"]
_LEVEL_UP_KEYS = ["level_5", "level_10", "level_20"]

_PREDICATES: dict[str, Any] = {
    "first_race": _pred_first_race,
    "perfect_race": _pred_perfect_race,
    "podium_finisher": _pred_podium_finisher,
    "champion": _pred_champion,
    "level_5": _pred_level_5,
    "level_10": _pred_level_10,
    "level_20": _pred_level_20,
}


# ── Domain service ────────────────────────────────────────────────────────────


def _to_response(key: str, unlocked_at: Any) -> AchievementResponse | None:
    defn = get_by_key(key)
    if defn is None:
        return None
    return AchievementResponse(
        key=defn.key,
        category=defn.category,
        title=defn.title,
        description=defn.description,
        hidden=defn.hidden,
        icon_path=defn.icon_path,
        unlocked_at=unlocked_at,
    )


class AchievementDomainService:
    def __init__(self, repository: AchievementRepository) -> None:
        self._repository = repository

    async def _evaluate_keys(
        self,
        keys: list[str],
        account_id: uuid.UUID,
        event_data: dict[str, Any],
        session: AsyncSession,
    ) -> list[AchievementResponse]:
        results: list[AchievementResponse] = []
        for key in keys:
            predicate = _PREDICATES.get(key)
            if predicate is None:
                continue
            try:
                qualifies = await predicate(account_id, event_data, session)
                if not qualifies:
                    continue
                record = await self._repository.unlock(account_id, key)
                if record is not None:
                    response = _to_response(key, record.unlocked_at)
                    if response is not None:
                        results.append(response)
            except Exception:
                logger.exception(
                    "Achievement predicate failed",
                    extra={"context": {"key": key, "account_id": str(account_id)}},
                )
        return results

    async def evaluate_race_completed(
        self,
        account_id: uuid.UUID,
        event_data: dict[str, Any],
        session: AsyncSession,
    ) -> list[AchievementResponse]:
        return await self._evaluate_keys(_RACE_COMPLETED_KEYS, account_id, event_data, session)

    async def evaluate_level_up(
        self,
        account_id: uuid.UUID,
        new_level: int,
        session: AsyncSession,
    ) -> list[AchievementResponse]:
        return await self._evaluate_keys(
            _LEVEL_UP_KEYS, account_id, {"new_level": new_level}, session
        )

    async def get_visible_catalogue(
        self,
        account_id: uuid.UUID | None,
        session: AsyncSession,
    ) -> list[AchievementResponse]:
        unlocked_map: dict[str, Any] = {}
        if account_id is not None:
            records = await self._repository.get_unlocked(account_id)
            unlocked_map = {r.achievement_key: r.unlocked_at for r in records}

        result: list[AchievementResponse] = []
        for defn in CATALOGUE:
            if defn.hidden and defn.key not in unlocked_map:
                continue
            result.append(
                AchievementResponse(
                    key=defn.key,
                    category=defn.category,
                    title=defn.title,
                    description=defn.description,
                    hidden=defn.hidden,
                    icon_path=defn.icon_path,
                    unlocked_at=unlocked_map.get(defn.key),
                )
            )
        return result
