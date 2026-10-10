"""Unit tests for ChampionshipDomainService pure logic."""

from __future__ import annotations

import uuid
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.championships.domain_service import _build_standings, _points_for_position
from app.championships.models import Championship
from app.championships.repository import SQLAlchemyChampionshipRepository
from app.shared.exceptions import ConflictError

# ── Points table ──────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "position,expected",
    [(1, 10), (2, 8), (3, 6), (4, 4), (5, 2), (6, 0)],
)
def test_points_for_position(position: int, expected: int) -> None:
    assert _points_for_position(position) == expected


# ── Standings calculation ─────────────────────────────────────────────────────


def _make_championship(race_rows: list[tuple[Any, ...]]) -> SimpleNamespace:
    """Create a duck-typed championship for testing _build_standings.

    race_rows: list of (avatar_id, is_player, finishing_position, points_earned)
    """
    rows = [
        SimpleNamespace(
            id=uuid.uuid4(),
            race_id=uuid.uuid4(),
            race_index=i,
            avatar_id=avatar_id,
            is_player=is_player,
            finishing_position=finishing_position,
            points_earned=points_earned,
        )
        for i, (avatar_id, is_player, finishing_position, points_earned) in enumerate(race_rows)
    ]
    return SimpleNamespace(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        total_races=3,
        races_completed=len(race_rows),
        status="active",
        championship_races=rows,
    )


def test_standings_single_race_correct_order() -> None:
    championship = _make_championship(
        [
            ("p1", True, 1, 10),
            ("ai1", False, 2, 8),
            ("ai2", False, 3, 6),
        ]
    )
    standings = _build_standings(championship)
    assert standings[0].avatar_id == "p1"
    assert standings[0].points == 10
    assert standings[0].position == 1
    assert standings[1].avatar_id == "ai1"
    assert standings[1].points == 8
    assert standings[2].avatar_id == "ai2"
    assert standings[2].points == 6


def test_standings_cumulative_across_races() -> None:
    championship = _make_championship(
        [
            ("p1", True, 2, 8),  # race 0
            ("ai1", False, 1, 10),
            ("p1", True, 1, 10),  # race 1
            ("ai1", False, 2, 8),
        ]
    )
    standings = _build_standings(championship)
    assert standings[0].avatar_id == "p1"
    assert standings[0].points == 18
    assert standings[1].avatar_id == "ai1"
    assert standings[1].points == 18
    # Tiebreak: podiums — p1 has 2 podiums (pos 2 + pos 1), ai1 has 2 (pos 1 + pos 2)
    # Both equal; order is stable (by insertion dict key order)


def test_standings_podium_count() -> None:
    championship = _make_championship(
        [
            ("p1", True, 1, 10),
            ("ai1", False, 4, 4),
        ]
    )
    standings = _build_standings(championship)
    player = next(s for s in standings if s.is_player)
    ai = next(s for s in standings if not s.is_player)
    assert player.podiums == 1
    assert ai.podiums == 0


def test_standings_tiebreak_by_podiums() -> None:
    championship = _make_championship(
        [
            ("p1", True, 3, 6),  # 6 pts, 1 podium
            ("ai1", False, 4, 4),  # 4 pts, 0 podiums — race 0
            ("p1", True, 3, 6),  # +6 = 12 pts, 2 podiums
            ("ai1", False, 1, 10),  # +10 = 11 pts, 1 podium
        ]
    )
    standings = _build_standings(championship)
    assert standings[0].avatar_id == "ai1"
    assert standings[0].points == 14


def test_standings_empty_returns_empty_list() -> None:
    championship = _make_championship([])
    assert _build_standings(championship) == []


def test_standings_position_field_is_1indexed() -> None:
    championship = _make_championship(
        [
            ("p1", True, 1, 10),
            ("ai1", False, 2, 8),
        ]
    )
    standings = _build_standings(championship)
    assert standings[0].position == 1
    assert standings[1].position == 2


@pytest.mark.asyncio
async def test_championship_rejects_placements_that_differ_from_saved_race() -> None:
    account_id = uuid.uuid4()
    child_id = uuid.uuid4()
    championship_id = uuid.uuid4()
    race_id = uuid.uuid4()
    persisted_race = SimpleNamespace(
        avatar_id="human",
        participants=[
            SimpleNamespace(avatar_id="human", position=2),
            SimpleNamespace(avatar_id="opponent", position=1),
        ],
    )
    result = MagicMock()
    result.scalar_one_or_none.return_value = persisted_race
    session = MagicMock()
    session.execute = AsyncMock(return_value=result)
    championship = Championship(
        id=championship_id,
        account_id=account_id,
        child_profile_id=child_id,
        total_races=3,
        races_completed=0,
        status="active",
        championship_races=[],
    )
    repository = SQLAlchemyChampionshipRepository(session)

    with pytest.raises(ConflictError, match="must match the saved race result"):
        await repository.add_race(
            championship,
            race_id,
            0,
            [
                {
                    "avatar_id": "human",
                    "is_player": True,
                    "finishing_position": 1,
                    "points_earned": 10,
                },
                {
                    "avatar_id": "opponent",
                    "is_player": False,
                    "finishing_position": 2,
                    "points_earned": 8,
                },
            ],
        )

    session.add.assert_not_called()
