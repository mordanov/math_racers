from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.mathematics.generator import generate_problem_set
from app.races.repository import SQLAlchemyRaceRepository
from app.races.schemas import (
    OperationAnswerRequest,
    ParticipantSummaryRequest,
    RaceAnswerSubmitRequest,
    RaceSummaryRequest,
)
from app.shared.exceptions import ConflictError, ValidationError

pytestmark = pytest.mark.unit


def _session(race: SimpleNamespace, answers: list[MagicMock]) -> MagicMock:
    race_result = MagicMock()
    race_result.scalar_one_or_none.return_value = race
    answer_result = MagicMock()
    answer_result.scalars.return_value.all.return_value = answers
    session = MagicMock()
    session.execute = AsyncMock(side_effect=[race_result, answer_result])
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


def _race(**overrides: object) -> SimpleNamespace:
    values: dict[str, object] = {
        "id": uuid.uuid4(),
        "account_id": uuid.uuid4(),
        "child_profile_id": uuid.uuid4(),
        "status": "active",
        "mode": "quick",
        "difficulty_tier": 2,
        "seed": "42",
        "started_at": datetime.now(UTC) - timedelta(seconds=2),
        "custom_tier_config": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


@pytest.mark.asyncio
async def test_answer_submission_stores_server_timing_and_correctness() -> None:
    race = _race()
    problem = generate_problem_set(2, 42, 8).problems[0]
    session = _session(race, [])
    request = RaceAnswerSubmitRequest(
        answer_index=0,
        operation=problem.operation.value,
        answer=str(problem.answer),
    )

    response = await SQLAlchemyRaceRepository(session).submit_answer(
        race.id, race.account_id, race.child_profile_id, request
    )

    saved = session.add.call_args.args[0]
    assert response.is_correct is True
    assert response.response_time_ms >= 0
    assert saved.submitted_answer == str(problem.answer)
    assert saved.answered_at is not None
    assert saved.problem_operand_a == problem.operand_a
    assert saved.problem_operand_b == problem.operand_b


@pytest.mark.asyncio
async def test_answer_retry_replays_saved_response_and_rejects_changed_answer() -> None:
    race = _race()
    problem = generate_problem_set(2, 42, 8).problems[0]
    answer = MagicMock(
        answer_index=0,
        operation=problem.operation.value,
        submitted_answer=str(problem.answer),
        is_correct=True,
        response_time_ms=1234,
        answered_at=datetime.now(UTC),
    )
    request = RaceAnswerSubmitRequest(
        answer_index=0,
        operation=problem.operation.value,
        answer=str(problem.answer),
    )
    repository = SQLAlchemyRaceRepository(_session(race, [answer]))

    response = await repository.submit_answer(
        race.id, race.account_id, race.child_profile_id, request
    )

    assert response.response_time_ms == 1234


@pytest.mark.asyncio
async def test_answer_submission_rejects_a_different_answer_for_a_saved_index() -> None:
    race = _race()
    problem = generate_problem_set(2, 42, 8).problems[0]
    answer = MagicMock(
        answer_index=0,
        operation=problem.operation.value,
        submitted_answer=str(problem.answer),
        is_correct=True,
        response_time_ms=1234,
        answered_at=datetime.now(UTC),
    )
    request = RaceAnswerSubmitRequest(
        answer_index=0,
        operation=problem.operation.value,
        answer=str(problem.answer + 1),
    )

    with pytest.raises(ConflictError, match="different content"):
        await SQLAlchemyRaceRepository(_session(race, [answer])).submit_answer(
            race.id, race.account_id, race.child_profile_id, request
        )


@pytest.mark.asyncio
async def test_answer_submission_requires_the_expected_next_index() -> None:
    race = _race()
    session = _session(race, [])
    request = RaceAnswerSubmitRequest(
        answer_index=1,
        operation="addition",
        answer="1",
    )

    with pytest.raises(ValidationError, match="submitted in order"):
        await SQLAlchemyRaceRepository(session).submit_answer(
            race.id, race.account_id, race.child_profile_id, request
        )


@pytest.mark.asyncio
async def test_training_result_persists_only_answers_missing_after_saved_prefix() -> None:
    race = _race(mode="training", avatar_id="avatar-1")
    race.created_at = datetime.now(UTC)
    problems = [generate_problem_set(2, 42 + index, 1).problems[0] for index in range(3)]
    saved_prefix = MagicMock(answer_index=0)
    session = _session(race, [saved_prefix])
    request = RaceSummaryRequest(
        human_avatar_id="avatar-1",
        race_id=race.id,
        child_profile_id=race.child_profile_id,
        idempotency_key=uuid.uuid4(),
        seed="42",
        difficulty_tier=2,
        mode="training",
        started_at=race.started_at,
        completed_at=datetime.now(UTC),
        participants=[
            ParticipantSummaryRequest(
                avatar_id="avatar-1",
                position=None,
                problems_correct=3,
                longest_streak=3,
                average_response_ms=1000,
                total_distance=0,
                xp_earned=0,
            )
        ],
        answers=[
            OperationAnswerRequest(
                operation=problem.operation.value,
                is_correct=True,
                response_time_ms=1000 + index,
                submitted_answer=str(problem.answer),
            )
            for index, problem in enumerate(problems)
        ],
    )

    await SQLAlchemyRaceRepository(session).create(request)

    saved_answers = [
        call.args[0]
        for call in session.add.call_args_list
        if call.args and getattr(call.args[0], "answer_index", None) is not None
    ]
    assert [answer.answer_index for answer in saved_answers] == [1, 2]
