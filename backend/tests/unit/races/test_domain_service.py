"""Unit tests for RaceDomainService."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.races.ai_scoring import simulate_opponents
from app.races.domain_service import RaceDomainService
from app.races.schemas import (
    ParticipantSummaryRequest,
    RaceResultAnswerRequest,
    RaceResultParticipantRequest,
    RaceResultRequest,
    RaceSummaryRequest,
    RaceSummaryResponse,
)
from app.shared.exceptions import ConflictError, PermissionError, ValidationError


def _make_request(**overrides: object) -> RaceSummaryRequest:
    defaults: dict[str, object] = {
        "race_id": uuid.uuid4(),
        "seed": "42",
        "difficulty_tier": 3,
        "mode": "quick",
        "human_avatar_id": "avatar-1",
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
async def test_statistics_failure_propagates_for_transaction_rollback() -> None:
    mock_repo = MagicMock()
    expected = RaceSummaryResponse(
        race_id=uuid.uuid4(), created_at=datetime(2026, 8, 10, tzinfo=UTC)
    )
    mock_repo.create = AsyncMock(return_value=expected)

    mock_stats = MagicMock()
    mock_stats.update_on_race = AsyncMock(side_effect=RuntimeError("db timeout"))

    service = RaceDomainService(mock_repo, statistics_service=mock_stats)
    with pytest.raises(RuntimeError, match="db timeout"):
        await service.persist_race(_make_request(), account_id=uuid.uuid4())

    mock_repo.create.assert_awaited_once()


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


@pytest.mark.asyncio
async def test_progression_and_statistics_use_human_avatar_not_first_place() -> None:
    account_id = uuid.uuid4()
    request = _make_request(
        human_avatar_id="human-avatar",
        participants=[
            ParticipantSummaryRequest(
                avatar_id="ai-avatar",
                position=1,
                problems_correct=8,
                longest_streak=5,
                average_response_ms=1000,
                total_distance=144,
                xp_earned=300,
            ),
            ParticipantSummaryRequest(
                avatar_id="human-avatar",
                position=2,
                problems_correct=2,
                longest_streak=1,
                average_response_ms=2000,
                total_distance=100,
                xp_earned=40,
            ),
        ],
    )
    mock_repo = MagicMock()
    mock_repo.create = AsyncMock(
        return_value=RaceSummaryResponse(
            race_id=request.race_id, created_at=datetime(2026, 8, 10, tzinfo=UTC)
        )
    )
    progression_repo = MagicMock()
    progression_repo.add_xp = AsyncMock(return_value=(140, 1))
    progression_repo.insert_event = AsyncMock()
    statistics_service = MagicMock()
    statistics_service.update_on_race = AsyncMock()

    service = RaceDomainService(
        mock_repo,
        progression_repository=progression_repo,
        statistics_service=statistics_service,
    )
    result = await service.persist_race(request, account_id=account_id)

    assert result.progression is not None
    assert result.progression.xp_earned_this_race == 140
    persisted_request = mock_repo.create.await_args.args[0]
    assert (
        next(p for p in persisted_request.participants if p.avatar_id == "human-avatar").xp_earned
        == 140
    )
    statistics_service.update_on_race.assert_awaited_once_with(account_id, request)


def test_result_contract_rejects_client_supplied_metrics_and_xp() -> None:
    from pydantic import ValidationError as PydanticValidationError

    from app.races.schemas import RaceResultRequest

    with pytest.raises(PydanticValidationError, match="Extra inputs are not permitted"):
        RaceResultRequest.model_validate(
            {
                "idempotency_key": str(uuid.uuid4()),
                "human_avatar_id": "avatar-1",
                "participants": [
                    {
                        "avatar_id": "avatar-1",
                        "position": 1,
                        "problems_correct": 6,
                        "longest_streak": 3,
                        "average_response_ms": 1800,
                        "total_distance": 100,
                        "xp_earned": 999999,
                    }
                ],
                "answers": [],
            }
        )


def test_result_contract_accepts_idempotency_key_and_operation_answers() -> None:
    from app.races.schemas import RaceResultRequest

    result = RaceResultRequest.model_validate(
        {
            "idempotency_key": str(uuid.uuid4()),
            "human_avatar_id": "avatar-1",
            "participants": [
                {
                    "avatar_id": "avatar-1",
                    "position": 2,
                }
            ],
            "answers": [
                {
                    "operation": "multiplication",
                    "answer": "6",
                    "response_time_ms": 1800,
                }
            ],
        }
    )
    assert result.participants[0].avatar_id == "avatar-1"
    assert result.answers[0].operation == "multiplication"


def test_race_session_contract_rejects_invalid_training_and_championship_modes() -> None:
    from pydantic import ValidationError as PydanticValidationError

    from app.races.schemas import RaceSessionRequest

    with pytest.raises(PydanticValidationError):
        RaceSessionRequest(
            mode="training",
            difficulty_tier=2,
            avatar_id=uuid.uuid4(),
            opponent_count=1,
        )
    with pytest.raises(PydanticValidationError):
        RaceSessionRequest(
            mode="championship",
            difficulty_tier=2,
            avatar_id=uuid.uuid4(),
            opponent_count=1,
        )
    with pytest.raises(PydanticValidationError):
        RaceSessionRequest.model_validate(
            {
                "mode": "quick",
                "difficulty_tier": 6,
                "avatar_id": str(uuid.uuid4()),
                "opponent_count": 0,
                "custom_tier_config": {
                    "operations": ["addition"],
                    "min_operand": 1,
                    "max_operand": 20,
                },
            }
        )


def test_tier6_race_session_rejects_client_supplied_settings() -> None:
    from pydantic import ValidationError as PydanticValidationError

    from app.races.schemas import RaceSessionRequest

    with pytest.raises(PydanticValidationError, match="Extra inputs are not permitted"):
        RaceSessionRequest.model_validate(
            {
                "mode": "quick",
                "difficulty_tier": 6,
                "avatar_id": str(uuid.uuid4()),
                "opponent_count": 0,
                "custom_tier_config": {
                    "operations": ["addition", "division"],
                    "min_operand": 2,
                    "max_operand": 50,
                },
            }
        )


def _saved_answers(
    seed: int = 42, tier: int = 2, *, incorrect_index: int | None = None
) -> list[MagicMock]:
    from app.mathematics.generator import generate_problem_set

    problems = generate_problem_set(tier, seed, 8).problems
    return [
        MagicMock(
            answer_index=index,
            operation=problem.operation.value,
            submitted_answer=str(problem.answer + (1 if index == incorrect_index else 0)),
            is_correct=index != incorrect_index,
            response_time_ms=1500,
            answered_at=datetime(2026, 8, 10, 12, 0, index + 1, tzinfo=UTC),
        )
        for index, problem in enumerate(problems)
    ]


def _make_result_request() -> RaceResultRequest:
    return RaceResultRequest(
        idempotency_key=uuid.uuid4(),
        human_avatar_id="avatar-1",
        participants=[
            RaceResultParticipantRequest(
                avatar_id="avatar-1",
                position=1,
            )
        ],
    )


@pytest.mark.asyncio
async def test_submit_training_result_uses_the_clients_per_problem_seed_sequence() -> None:
    from app.mathematics.generator import generate_problem_set

    seed = 42
    problems = [generate_problem_set(2, seed, 1).problems[0]]
    for index in range(1, 10):
        previous = problems[-1]
        candidate_seed = seed + index
        candidate = generate_problem_set(2, candidate_seed, 1).problems[0]
        attempt = 0
        while (
            candidate.operation == previous.operation
            and candidate.operand_a == previous.operand_a
            and candidate.operand_b == previous.operand_b
            and attempt < 100
        ):
            attempt += 1
            candidate_seed = seed + index + attempt * 104729
            candidate = generate_problem_set(2, candidate_seed, 1).problems[0]
        problems.append(candidate)

    account_id = uuid.uuid4()
    child_id = uuid.uuid4()
    race_id = uuid.uuid4()
    started_at = datetime(2026, 8, 10, 12, tzinfo=UTC)
    request = RaceResultRequest(
        idempotency_key=uuid.uuid4(),
        human_avatar_id="avatar-1",
        participants=[
            RaceResultParticipantRequest(
                avatar_id="avatar-1",
                position=None,
            )
        ],
        answers=[
            RaceResultAnswerRequest(
                operation=problem.operation.value,
                answer=str(problem.answer),
                response_time_ms=1500,
            )
            for problem in problems
        ],
    )
    race = MagicMock(
        account_id=account_id,
        child_profile_id=child_id,
        avatar_id="avatar-1",
        status="active",
        id=race_id,
        seed=str(seed),
        difficulty_tier=2,
        mode="training",
        opponent_count=0,
        started_at=started_at,
        custom_tier_config=None,
    )
    repo = MagicMock()
    repo.get_session_for_update = AsyncMock(return_value=race)
    repo.list_answers = AsyncMock(return_value=[])
    repo.create = AsyncMock(
        return_value=RaceSummaryResponse(
            race_id=race_id, created_at=datetime(2026, 8, 10, tzinfo=UTC)
        )
    )
    repo.save_result_response = AsyncMock()

    result = await RaceDomainService(repo).submit_result(
        race_id, account_id, child_id, request, MagicMock()
    )

    assert result.race_id == race_id
    saved_summary = repo.create.await_args.args[0]
    assert len(saved_summary.answers) == 10
    assert all(answer.is_correct for answer in saved_summary.answers)


@pytest.mark.asyncio
async def test_race_result_rejects_client_claimed_ai_win_and_uses_server_ai_metrics() -> None:
    account_id = uuid.uuid4()
    child_id = uuid.uuid4()
    race_id = uuid.uuid4()
    request = _make_result_request()
    request = request.model_copy(
        update={
            "participants": [
                RaceResultParticipantRequest(
                    avatar_id="avatar-1",
                    position=2,
                ),
                RaceResultParticipantRequest(
                    avatar_id="ai-1",
                    position=1,
                ),
            ]
        }
    )
    race = MagicMock(
        account_id=account_id,
        child_profile_id=child_id,
        avatar_id="avatar-1",
        status="active",
        id=race_id,
        seed="42",
        difficulty_tier=2,
        mode="quick",
        opponent_count=1,
        started_at=datetime(2026, 8, 10, 12, tzinfo=UTC),
        custom_tier_config=None,
    )
    repo = MagicMock()
    repo.get_session_for_update = AsyncMock(return_value=race)
    repo.list_answers = AsyncMock(return_value=_saved_answers())
    repo.create = AsyncMock(
        return_value=RaceSummaryResponse(
            race_id=race_id, created_at=datetime(2026, 8, 10, tzinfo=UTC)
        )
    )
    repo.save_result_response = AsyncMock()
    service = RaceDomainService(repo)

    with pytest.raises(ValidationError, match="positions do not match"):
        await service.submit_result(race_id, account_id, child_id, request, MagicMock())

    request.participants[0].position = 1
    request.participants[1].position = 2
    await service.submit_result(race_id, account_id, child_id, request, MagicMock())
    saved_summary = repo.create.await_args.args[0]
    saved_ai = next(p for p in saved_summary.participants if p.avatar_id == "ai-1")
    expected_ai = simulate_opponents(42, 1)[0]
    assert saved_ai.total_distance == expected_ai.total_distance
    assert saved_ai.total_distance < 999


@pytest.mark.asyncio
async def test_submit_result_uses_stored_session_and_persists_replay_response() -> None:
    account_id = uuid.uuid4()
    child_id = uuid.uuid4()
    race_id = uuid.uuid4()
    created_at = datetime(2026, 8, 10, 12, tzinfo=UTC)
    race = MagicMock(
        account_id=account_id,
        child_profile_id=child_id,
        avatar_id="avatar-1",
        status="active",
        id=race_id,
        seed="42",
        difficulty_tier=2,
        mode="quick",
        opponent_count=0,
        started_at=datetime(2026, 8, 10, 12, tzinfo=UTC),
    )
    repo = MagicMock()
    repo.get_session_for_update = AsyncMock(return_value=race)
    repo.list_answers = AsyncMock(return_value=_saved_answers())
    repo.create = AsyncMock(
        return_value=RaceSummaryResponse(race_id=race_id, created_at=created_at)
    )
    repo.save_result_response = AsyncMock()
    service = RaceDomainService(repo)
    request = _make_result_request()

    response = await service.submit_result(race_id, account_id, child_id, request, MagicMock())

    assert response.race_id == race_id
    stored_request = repo.create.await_args.args[0]
    assert stored_request.seed == "42"
    assert stored_request.mode == "quick"
    assert stored_request.started_at == race.started_at
    repo.save_result_response.assert_awaited_once_with(
        race_id,
        request.model_dump(mode="json"),
        response.model_dump(mode="json"),
    )


@pytest.mark.asyncio
async def test_submit_result_replays_identical_completed_result_without_side_effects() -> None:
    request = _make_result_request()
    response = RaceSummaryResponse(
        race_id=uuid.uuid4(),
        created_at=datetime(2026, 8, 10, 12, tzinfo=UTC),
    )
    race = MagicMock(
        account_id=uuid.uuid4(),
        child_profile_id=uuid.uuid4(),
        avatar_id="avatar-1",
        status="completed",
        id=uuid.uuid4(),
        idempotency_key=request.idempotency_key,
        result_payload=request.model_dump(mode="json"),
        result_response=response.model_dump(mode="json"),
    )
    repo = MagicMock()
    repo.get_session_for_update = AsyncMock(return_value=race)
    repo.list_answers = AsyncMock(return_value=_saved_answers())
    service = RaceDomainService(repo)

    result = await service.submit_result(
        race.id, race.account_id, race.child_profile_id, request, MagicMock()
    )

    assert result == response
    repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_submit_result_rejects_wrong_child_owner() -> None:
    race = MagicMock(
        account_id=uuid.uuid4(),
        child_profile_id=uuid.uuid4(),
        status="active",
        id=uuid.uuid4(),
    )
    repo = MagicMock()
    repo.get_session_for_update = AsyncMock(return_value=race)
    repo.list_answers = AsyncMock(return_value=_saved_answers())
    service = RaceDomainService(repo)

    with pytest.raises(PermissionError, match="does not belong"):
        await service.submit_result(
            race.id,
            race.account_id,
            uuid.uuid4(),
            _make_result_request(),
            MagicMock(),
        )


@pytest.mark.asyncio
async def test_submit_result_uses_server_derived_human_metrics() -> None:
    account_id = uuid.uuid4()
    child_id = uuid.uuid4()
    race = MagicMock(
        account_id=account_id,
        child_profile_id=child_id,
        avatar_id="avatar-1",
        status="active",
        id=uuid.uuid4(),
        seed="42",
        difficulty_tier=2,
        mode="quick",
        opponent_count=0,
        started_at=datetime(2026, 8, 10, 12, tzinfo=UTC),
    )
    repo = MagicMock()
    repo.get_session_for_update = AsyncMock(return_value=race)
    repo.list_answers = AsyncMock(return_value=_saved_answers())
    repo.create = AsyncMock(
        return_value=RaceSummaryResponse(
            race_id=race.id, created_at=datetime(2026, 8, 10, tzinfo=UTC)
        )
    )
    repo.save_result_response = AsyncMock()
    request = _make_result_request()

    await RaceDomainService(repo).submit_result(race.id, account_id, child_id, request, MagicMock())
    saved_summary = repo.create.await_args.args[0]
    assert saved_summary.participants[0].total_distance == 144


@pytest.mark.asyncio
async def test_submit_result_derives_correctness_from_server_generated_questions() -> None:
    account_id = uuid.uuid4()
    child_id = uuid.uuid4()
    race = MagicMock(
        account_id=account_id,
        child_profile_id=child_id,
        avatar_id="avatar-1",
        status="active",
        id=uuid.uuid4(),
        seed="42",
        difficulty_tier=2,
        mode="quick",
        opponent_count=0,
        started_at=datetime(2026, 8, 10, 12, tzinfo=UTC),
    )
    repo = MagicMock()
    repo.get_session_for_update = AsyncMock(return_value=race)
    repo.list_answers = AsyncMock(return_value=_saved_answers(incorrect_index=0))
    repo.create = AsyncMock(
        return_value=RaceSummaryResponse(
            race_id=race.id,
            created_at=datetime(2026, 8, 10, 12, tzinfo=UTC),
        )
    )
    repo.save_result_response = AsyncMock()
    request = _make_result_request()

    await RaceDomainService(repo).submit_result(race.id, account_id, child_id, request, MagicMock())

    saved_request = repo.create.await_args.args[0]
    saved_answers = saved_request.answers
    assert saved_answers[0].is_correct is False
    assert sum(answer.is_correct for answer in saved_answers) == 7
    assert saved_request.participants[0].problems_correct == 7
    assert saved_request.participants[0].longest_streak == 7
    assert saved_request.participants[0].total_distance == 126
