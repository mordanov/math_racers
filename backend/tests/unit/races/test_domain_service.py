"""Unit tests for RaceDomainService."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.races.domain_service import RaceDomainService
from app.races.schemas import ParticipantSummaryRequest, RaceSummaryRequest, RaceSummaryResponse
from app.shared.exceptions import ConflictError, ValidationError


def _make_request(**overrides: object) -> RaceSummaryRequest:
    defaults: dict[str, object] = {
        "race_id": uuid.uuid4(),
        "seed": "42",
        "difficulty_tier": 3,
        "mode": "quick",
        "started_at": datetime(2026, 8, 10, 12, 0, 0, tzinfo=UTC),
        "completed_at": datetime(2026, 8, 10, 12, 5, 0, tzinfo=UTC),
        "participants": [
            ParticipantSummaryRequest(
                avatar_id="avatar-1",
                position=1,
                problems_correct=8,
                longest_streak=0,
                average_response_ms=1500,
                total_distance=144,
                xp_earned=100,
            )
        ],
    }
    defaults.update(overrides)
    return RaceSummaryRequest(**defaults)


@pytest.mark.asyncio
async def test_persist_race_calls_repository() -> None:
    mock_repo = MagicMock()
    expected = RaceSummaryResponse(
        race_id=uuid.uuid4(), created_at=datetime(2026, 8, 10, tzinfo=UTC)
    )
    mock_repo.create = AsyncMock(return_value=expected)

    service = RaceDomainService(mock_repo)
    request = _make_request()
    result = await service.persist_race(request)

    mock_repo.create.assert_awaited_once_with(request)
    assert result == expected


@pytest.mark.asyncio
async def test_duplicate_race_id_raises_conflict() -> None:
    mock_repo = MagicMock()
    mock_repo.create = AsyncMock(
        side_effect=ConflictError(error_code="RACE_ALREADY_EXISTS", message="already exists")
    )

    service = RaceDomainService(mock_repo)
    with pytest.raises(ConflictError, match="already exists"):
        await service.persist_race(_make_request())


@pytest.mark.asyncio
async def test_non_unique_positions_raise_validation_error() -> None:
    request = _make_request(
        participants=[
            ParticipantSummaryRequest(
                avatar_id="a1",
                position=1,
                problems_correct=4,
                longest_streak=0,
                average_response_ms=2000,
                total_distance=72,
                xp_earned=50,
            ),
            ParticipantSummaryRequest(
                avatar_id="a2",
                position=1,
                problems_correct=6,
                longest_streak=0,
                average_response_ms=1800,
                total_distance=90,
                xp_earned=60,
            ),
        ]
    )
    mock_repo = MagicMock()
    service = RaceDomainService(mock_repo)
    with pytest.raises(ValidationError):
        await service.persist_race(request)


def test_training_participant_requires_null_position() -> None:
    from pydantic import ValidationError as PydanticValidationError

    with pytest.raises(PydanticValidationError):
        _make_request(
            mode="training",
            participants=[
                ParticipantSummaryRequest(
                    avatar_id="a1",
                    position=1,  # must be null for training
                    problems_correct=5,
                    longest_streak=0,
                    average_response_ms=1500,
                    total_distance=90,
                    xp_earned=25,
                )
            ],
        )


def test_training_participant_with_null_position_is_valid() -> None:
    request = _make_request(
        mode="training",
        participants=[
            ParticipantSummaryRequest(
                avatar_id="a1",
                position=None,
                problems_correct=5,
                longest_streak=0,
                average_response_ms=1500,
                total_distance=90,
                xp_earned=25,
            )
        ],
    )
    assert request.participants[0].position is None


def test_non_training_participant_requires_non_null_position() -> None:
    from pydantic import ValidationError as PydanticValidationError

    with pytest.raises(PydanticValidationError):
        _make_request(
            mode="quick",
            participants=[
                ParticipantSummaryRequest(
                    avatar_id="a1",
                    position=None,  # must not be null for non-training
                    problems_correct=5,
                    longest_streak=0,
                    average_response_ms=1500,
                    total_distance=90,
                    xp_earned=25,
                )
            ],
        )


@pytest.mark.asyncio
async def test_valid_multi_participant_race_passes_validation() -> None:
    request = _make_request(
        participants=[
            ParticipantSummaryRequest(
                avatar_id="a1",
                position=1,
                problems_correct=8,
                longest_streak=0,
                average_response_ms=1500,
                total_distance=144,
                xp_earned=100,
            ),
            ParticipantSummaryRequest(
                avatar_id="a2",
                position=2,
                problems_correct=6,
                longest_streak=0,
                average_response_ms=2500,
                total_distance=108,
                xp_earned=70,
            ),
        ]
    )
    mock_repo = MagicMock()
    expected = RaceSummaryResponse(
        race_id=request.race_id,
        created_at=datetime(2026, 8, 10, tzinfo=UTC),
    )
    mock_repo.create = AsyncMock(return_value=expected)

    service = RaceDomainService(mock_repo)
    result = await service.persist_race(request)
    assert result == expected
