from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from app.championships.schemas import ChampionshipResponse, StandingEntry
from app.shared.exceptions import PermissionError, ValidationError

if TYPE_CHECKING:
    from app.championships.models import Championship
    from app.championships.repository import ChampionshipRepository
    from app.championships.schemas import CreateChampionshipRequest, RecordRaceRequest

_POINTS_TABLE = [10, 6, 3, 1, 0]


def _points_for_position(position: int) -> int:
    idx = position - 1
    return _POINTS_TABLE[idx] if 0 <= idx < len(_POINTS_TABLE) else 0


def _build_standings(championship: Any) -> list[StandingEntry]:
    totals: dict[str, dict[str, Any]] = {}
    for cr in championship.championship_races:
        if cr.avatar_id not in totals:
            totals[cr.avatar_id] = {
                "avatar_id": cr.avatar_id,
                "is_player": cr.is_player,
                "points": 0,
                "podiums": 0,
            }
        totals[cr.avatar_id]["points"] += cr.points_earned
        if cr.finishing_position <= 3:
            totals[cr.avatar_id]["podiums"] += 1

    sorted_entries = sorted(totals.values(), key=lambda e: (-e["points"], -e["podiums"]))
    return [
        StandingEntry(
            avatar_id=e["avatar_id"],
            is_player=e["is_player"],
            points=e["points"],
            podiums=e["podiums"],
            position=pos + 1,
        )
        for pos, e in enumerate(sorted_entries)
    ]


def _to_response(championship: Championship) -> ChampionshipResponse:
    return ChampionshipResponse(
        championship_id=championship.id,
        total_races=championship.total_races,
        races_completed=championship.races_completed,
        status=championship.status,
        standings=_build_standings(championship),
        created_at=championship.created_at,
    )


class ChampionshipDomainService:
    def __init__(self, repository: ChampionshipRepository) -> None:
        self._repository = repository

    async def create(
        self, account_id: uuid.UUID, request: CreateChampionshipRequest
    ) -> ChampionshipResponse:
        championship = await self._repository.create(account_id, request.total_races)
        return _to_response(championship)

    async def get(self, account_id: uuid.UUID, championship_id: uuid.UUID) -> ChampionshipResponse:
        championship = await self._repository.get(championship_id)
        if championship.account_id != account_id:
            raise PermissionError(
                error_code="CHAMPIONSHIP_ACCESS_DENIED",
                message="You do not own this championship.",
            )
        return _to_response(championship)

    async def record_race(
        self,
        account_id: uuid.UUID,
        championship_id: uuid.UUID,
        race_id: uuid.UUID,
        request: RecordRaceRequest,
    ) -> ChampionshipResponse:
        championship = await self._repository.get(championship_id)
        if championship.account_id != account_id:
            raise PermissionError(
                error_code="CHAMPIONSHIP_ACCESS_DENIED",
                message="You do not own this championship.",
            )
        if championship.status == "completed":
            raise ValidationError(message="Championship is already completed.")

        player_entries = [p for p in request.participants if p.is_player]
        if len(player_entries) != 1:
            raise ValidationError(message="Exactly one participant must have is_player=true.")

        participants = [
            {
                "avatar_id": p.avatar_id,
                "is_player": p.is_player,
                "finishing_position": p.finishing_position,
                "points_earned": _points_for_position(p.finishing_position),
            }
            for p in request.participants
        ]

        championship = await self._repository.add_race(
            championship, race_id, request.race_index, participants
        )
        return _to_response(championship)
