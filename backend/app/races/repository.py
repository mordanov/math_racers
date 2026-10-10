from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.avatars.models import Avatar
from app.championships.models import Championship
from app.races.models import Race, RaceAnswer, RaceParticipant
from app.races.schemas import (
    RaceAnswerSubmitRequest,
    RaceAnswerSubmitResponse,
    RaceSessionRequest,
    RaceSessionResponse,
    RaceSummaryRequest,
    RaceSummaryResponse,
)
from app.shared.exceptions import ConflictError, NotFoundError, PermissionError, ValidationError


class RaceRepository(Protocol):
    async def create(self, request: RaceSummaryRequest) -> RaceSummaryResponse: ...
    async def create_session(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID, request: RaceSessionRequest
    ) -> RaceSessionResponse: ...
    async def get_session(self, race_id: uuid.UUID) -> Race | None: ...
    async def get_session_for_update(self, race_id: uuid.UUID) -> Race | None: ...
    async def list_answers(self, race_id: uuid.UUID) -> list[RaceAnswer]: ...
    async def submit_answer(
        self,
        race_id: uuid.UUID,
        account_id: uuid.UUID,
        child_profile_id: uuid.UUID,
        request: RaceAnswerSubmitRequest,
    ) -> RaceAnswerSubmitResponse: ...
    async def save_result_response(
        self, race_id: uuid.UUID, payload: dict[str, object], response: dict[str, object]
    ) -> None: ...


class SQLAlchemyRaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, request: RaceSummaryRequest) -> RaceSummaryResponse:
        existing = await self.get_session(request.race_id)
        if existing is None:
            raise NotFoundError(
                error_code="RACE_SESSION_NOT_FOUND",
                message=f"Race session {request.race_id} not found.",
            )
        if existing.status != "active":
            raise ConflictError(
                error_code="RACE_ALREADY_COMPLETED",
                message=f"Race session {request.race_id} is not active.",
            )

        if existing.avatar_id != request.human_avatar_id:
            raise PermissionError(
                error_code="RACE_HUMAN_MISMATCH",
                message="The submitted human avatar does not match the race session.",
            )

        existing.completed_at = request.completed_at
        existing.status = "completed"
        existing.idempotency_key = request.idempotency_key
        existing.result_payload = request.model_dump(mode="json")

        for p in request.participants:
            participant = RaceParticipant(
                race_id=existing.id,
                avatar_id=p.avatar_id,
                position=p.position,
                problems_correct=p.problems_correct,
                longest_streak=p.longest_streak,
                average_response_ms=p.average_response_ms,
                total_distance=p.total_distance,
                xp_earned=p.xp_earned,
            )
            self._session.add(participant)

        if request.mode == "training" and not await self.list_answers(existing.id):
            for index, answer in enumerate(request.answers):
                self._session.add(
                    RaceAnswer(
                        race_id=existing.id,
                        answer_index=index,
                        operation=answer.operation,
                        submitted_answer=answer.submitted_answer,
                        is_correct=answer.is_correct,
                        response_time_ms=answer.response_time_ms,
                    )
                )

        await self._session.flush()
        await self._session.refresh(existing)

        return RaceSummaryResponse(race_id=existing.id, created_at=existing.created_at)

    async def create_session(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID, request: RaceSessionRequest
    ) -> RaceSessionResponse:
        from app.mathematics.models import PlayerDifficulty
        from app.shared.exceptions import ValidationError

        avatar_id = request.avatar_id

        avatar_result = await self._session.execute(
            select(Avatar).where(
                Avatar.id == avatar_id,
                Avatar.account_id == account_id,
                Avatar.child_profile_id == child_profile_id,
            )
        )
        if avatar_result.scalar_one_or_none() is None:
            raise NotFoundError("AVATAR_NOT_FOUND", "Avatar not found.")
        if request.championship_id is not None:
            championship_result = await self._session.execute(
                select(Championship).where(
                    Championship.id == request.championship_id,
                    Championship.account_id == account_id,
                    Championship.child_profile_id == child_profile_id,
                    Championship.status == "active",
                )
            )
            if championship_result.scalar_one_or_none() is None:
                raise NotFoundError("CHAMPIONSHIP_NOT_FOUND", "Championship not found.")

        custom_tier_config = None
        if request.difficulty_tier == 6:
            difficulty_result = await self._session.execute(
                select(PlayerDifficulty).where(PlayerDifficulty.player_id == account_id)
            )
            difficulty = difficulty_result.scalar_one_or_none()
            if difficulty is None or difficulty.custom_tier_config is None:
                raise ValidationError(
                    "TIER_6_SETTINGS_REQUIRED",
                    "Save parent Tier 6 settings before starting this race.",
                )
            custom_tier_config = difficulty.custom_tier_config

        seed = secrets.randbits(32)
        now = datetime.now(UTC)
        race = Race(
            account_id=account_id,
            child_profile_id=child_profile_id,
            avatar_id=str(request.avatar_id),
            opponent_count=request.opponent_count,
            custom_tier_config=custom_tier_config,
            championship_id=request.championship_id,
            seed=str(seed),
            difficulty_tier=request.difficulty_tier,
            mode=request.mode,
            started_at=now,
            completed_at=now,
            status="active",
        )
        self._session.add(race)
        await self._session.flush()
        return RaceSessionResponse(race_id=race.id, seed=seed)

    async def get_session(self, race_id: uuid.UUID) -> Race | None:
        result = await self._session.execute(select(Race).where(Race.id == race_id))
        return result.scalar_one_or_none()

    async def get_session_for_update(self, race_id: uuid.UUID) -> Race | None:
        result = await self._session.execute(
            select(Race).where(Race.id == race_id).with_for_update()
        )
        return result.scalar_one_or_none()

    async def list_answers(self, race_id: uuid.UUID) -> list[RaceAnswer]:
        result = await self._session.execute(
            select(RaceAnswer)
            .where(RaceAnswer.race_id == race_id)
            .order_by(RaceAnswer.answer_index, RaceAnswer.id)
        )
        return list(result.scalars().all())

    async def submit_answer(
        self,
        race_id: uuid.UUID,
        account_id: uuid.UUID,
        child_profile_id: uuid.UUID,
        request: RaceAnswerSubmitRequest,
    ) -> RaceAnswerSubmitResponse:
        from app.mathematics.generator import generate_problem_set
        from app.mathematics.tiers import TierConfig
        from app.mathematics.types import Operation

        race = await self.get_session_for_update(race_id)
        if race is None:
            raise NotFoundError("RACE_SESSION_NOT_FOUND", "Race session not found.")
        if race.account_id != account_id or race.child_profile_id != child_profile_id:
            raise PermissionError("FORBIDDEN", "Race session does not belong to this child.")
        if race.status != "active":
            raise ConflictError("RACE_NOT_ACTIVE", "Race session is not active.")
        if race.mode != "training" and request.answer_index >= 8:
            raise ValidationError("RACE_ANSWER_LIMIT", "Competitive races have eight answers.")

        answers = await self.list_answers(race_id)
        if request.answer_index < len(answers):
            saved = answers[request.answer_index]
            if (
                saved.answer_index == request.answer_index
                and saved.operation == request.operation
                and saved.submitted_answer == request.answer
                and saved.answered_at is not None
            ):
                return RaceAnswerSubmitResponse(
                    answer_index=request.answer_index,
                    is_correct=saved.is_correct,
                    response_time_ms=saved.response_time_ms,
                )
            raise ConflictError(
                "RACE_ANSWER_CONFLICT",
                "An answer already exists at this index with different content.",
            )
        if request.answer_index != len(answers):
            raise ValidationError("RACE_ANSWER_ORDER", "Answers must be submitted in order.")

        custom_config = None
        if isinstance(race.custom_tier_config, dict):
            from app.races.schemas import CustomTierConfigRequest

            saved_config = CustomTierConfigRequest.model_validate(race.custom_tier_config)
            custom_config = TierConfig(
                tier=race.difficulty_tier,
                operations=tuple(Operation(value) for value in saved_config.operations),
                min_operand=saved_config.min_operand,
                max_operand=saved_config.max_operand,
            )

        if race.mode == "training":
            candidate_seed = int(race.seed) + request.answer_index
            problem = generate_problem_set(
                race.difficulty_tier, candidate_seed, 1, custom_config
            ).problems[0]
            if answers:
                previous = answers[-1]
                attempt = 0
                while (
                    previous.problem_operand_a is not None
                    and previous.problem_operand_b is not None
                    and (problem.operation.value, problem.operand_a, problem.operand_b)
                    == (
                        previous.operation,
                        previous.problem_operand_a,
                        previous.problem_operand_b,
                    )
                    and attempt < 100
                ):
                    attempt += 1
                    problem = generate_problem_set(
                        race.difficulty_tier,
                        candidate_seed + attempt * 104729,
                        1,
                        custom_config,
                    ).problems[0]
                if (
                    previous.problem_operand_a is not None
                    and previous.problem_operand_b is not None
                    and (problem.operation.value, problem.operand_a, problem.operand_b)
                    == (
                        previous.operation,
                        previous.problem_operand_a,
                        previous.problem_operand_b,
                    )
                ):
                    raise ValidationError(
                        "TRAINING_PROBLEM_GENERATION_FAILED",
                        "A distinct Training problem could not be generated.",
                    )
        else:
            problem = generate_problem_set(
                race.difficulty_tier, int(race.seed), 8, custom_config
            ).problems[request.answer_index]
        if request.operation != problem.operation.value:
            raise ValidationError(
                "RACE_ANSWER_OPERATION_MISMATCH",
                "The submitted operation does not match the race question.",
            )

        try:
            submitted_answer = int(request.answer.strip())
        except ValueError:
            is_correct = False
        else:
            is_correct = submitted_answer == problem.answer

        now = datetime.now(UTC)
        previous_time = answers[-1].answered_at if answers else race.started_at
        if previous_time is None:
            raise ConflictError(
                "RACE_ANSWER_TIMESTAMP_MISSING", "The prior answer time is missing."
            )
        response_time_ms = max(0, int((now - previous_time).total_seconds() * 1000))
        answer = RaceAnswer(
            race_id=race.id,
            answer_index=request.answer_index,
            problem_operand_a=problem.operand_a,
            problem_operand_b=problem.operand_b,
            operation=request.operation,
            submitted_answer=request.answer,
            is_correct=is_correct,
            response_time_ms=response_time_ms,
            answered_at=now,
        )
        self._session.add(answer)
        await self._session.flush()
        return RaceAnswerSubmitResponse(
            answer_index=request.answer_index,
            is_correct=is_correct,
            response_time_ms=response_time_ms,
        )

    async def save_result_response(
        self, race_id: uuid.UUID, payload: dict[str, object], response: dict[str, object]
    ) -> None:
        race = await self.get_session(race_id)
        if race is None:
            raise NotFoundError("RACE_SESSION_NOT_FOUND", "Race session not found.")
        race.result_payload = payload
        race.result_response = response
        await self._session.flush()
