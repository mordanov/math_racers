from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.mathematics.tiers import TierConfig
from app.mathematics.types import Problem, ProblemSet
from app.races.ai_scoring import OpponentResult, simulate_opponents
from app.shared.exceptions import ValidationError

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.achievements.repository import AchievementRepository
    from app.progression.repository import ProgressionRepository
    from app.races.repository import RaceRepository
    from app.races.schemas import (
        RaceAnswerSubmitRequest,
        RaceAnswerSubmitResponse,
        RaceResultRequest,
        RaceSessionRequest,
        RaceSessionResponse,
        RaceSummaryRequest,
        RaceSummaryResponse,
    )
    from app.statistics.domain_service import StatisticsDomainService


def _generate_training_problems(
    generate: Callable[[int, int, int, TierConfig | None], ProblemSet],
    tier: int,
    seed: int,
    count: int,
    custom_tier_config: TierConfig | None,
) -> tuple[Problem, ...]:
    problems: list[Problem] = []
    while len(problems) < count:
        index = len(problems)
        candidate = generate(tier, seed + index, 1, custom_tier_config).problems[0]
        attempt = 0
        while (
            problems
            and (candidate.operation, candidate.operand_a, candidate.operand_b)
            == (
                problems[-1].operation,
                problems[-1].operand_a,
                problems[-1].operand_b,
            )
            and attempt < 100
        ):
            attempt += 1
            candidate = generate(
                tier, seed + index + attempt * 104729, 1, custom_tier_config
            ).problems[0]
        if problems and (candidate.operation, candidate.operand_a, candidate.operand_b) == (
            problems[-1].operation,
            problems[-1].operand_a,
            problems[-1].operand_b,
        ):
            raise ValueError("Unable to generate a distinct Training problem.")
        problems.append(candidate)
    return tuple(problems)


class RaceDomainService:
    def __init__(
        self,
        repository: RaceRepository,
        progression_repository: ProgressionRepository | None = None,
        achievement_repository: AchievementRepository | None = None,
        statistics_service: StatisticsDomainService | None = None,
    ) -> None:
        self._repository = repository
        self._progression_repository = progression_repository
        self._achievement_repository = achievement_repository
        self._statistics_service = statistics_service

    async def create_session(
        self,
        account_id: uuid.UUID,
        child_profile_id: uuid.UUID,
        request: RaceSessionRequest,
    ) -> RaceSessionResponse:
        return await self._repository.create_session(account_id, child_profile_id, request)

    async def submit_answer(
        self,
        race_id: uuid.UUID,
        account_id: uuid.UUID,
        child_profile_id: uuid.UUID,
        request: RaceAnswerSubmitRequest,
    ) -> RaceAnswerSubmitResponse:
        return await self._repository.submit_answer(race_id, account_id, child_profile_id, request)

    async def submit_result(
        self,
        race_id: uuid.UUID,
        account_id: uuid.UUID,
        child_profile_id: uuid.UUID,
        request: RaceResultRequest,
        session: AsyncSession,
    ) -> RaceSummaryResponse:
        from app.races.schemas import (
            OperationAnswerRequest,
            ParticipantSummaryRequest,
            RaceSummaryRequest,
            RaceSummaryResponse,
        )

        race = await self._repository.get_session_for_update(race_id)
        if race is None:
            from app.shared.exceptions import NotFoundError

            raise NotFoundError("RACE_SESSION_NOT_FOUND", "Race session not found.")
        if race.account_id != account_id or race.child_profile_id != child_profile_id:
            from app.shared.exceptions import PermissionError

            raise PermissionError("FORBIDDEN", "Race session does not belong to this child.")

        payload = request.model_dump(mode="json")
        if race.status == "completed":
            if (
                race.idempotency_key == request.idempotency_key
                and race.result_payload == payload
                and race.result_response is not None
            ):
                return RaceSummaryResponse.model_validate(race.result_response)
            from app.shared.exceptions import ConflictError

            raise ConflictError(
                "RACE_ALREADY_COMPLETED", "Race result conflicts with saved result."
            )
        if race.status != "active":
            from app.shared.exceptions import ConflictError

            raise ConflictError("RACE_NOT_ACTIVE", "Race session is not active.")
        if race.mode != "training" and request.answers:
            raise ValidationError(
                "CLIENT_ANSWERS_NOT_ALLOWED",
                "Competitive race answers must be submitted to the answer endpoint.",
            )
        if race.avatar_id != request.human_avatar_id:
            raise ValidationError(
                "RACE_HUMAN_MISMATCH", "Human avatar does not match race session."
            )
        if sum(p.avatar_id == request.human_avatar_id for p in request.participants) != 1:
            raise ValidationError(
                "INVALID_RACE_PARTICIPANTS",
                "Race result must contain the session avatar exactly once.",
            )
        expected_participants = (race.opponent_count or 0) + 1
        participant_ids = [participant.avatar_id for participant in request.participants]
        expected_avatar_ids = {
            request.human_avatar_id,
            *(f"ai-{index}" for index in range(1, expected_participants)),
        }
        if (
            len(request.participants) != expected_participants
            or len(participant_ids) != len(set(participant_ids))
            or set(participant_ids) != expected_avatar_ids
        ):
            raise ValidationError(
                "INVALID_RACE_PARTICIPANTS",
                "Race result participants do not match the saved session.",
            )

        from app.mathematics.generator import generate_problem_set
        from app.mathematics.tiers import TierConfig
        from app.mathematics.types import Operation
        from app.races.schemas import CustomTierConfigRequest

        custom_tier_config = None
        stored_config = getattr(race, "custom_tier_config", None)
        if isinstance(stored_config, dict):
            parsed_config = CustomTierConfigRequest.model_validate(stored_config)
            custom_tier_config = TierConfig(
                tier=race.difficulty_tier,
                operations=tuple(Operation(operation) for operation in parsed_config.operations),
                min_operand=parsed_config.min_operand,
                max_operand=parsed_config.max_operand,
            )
        saved_answers = await self._repository.list_answers(race.id)
        if race.mode != "training" and len(saved_answers) != 8:
            raise ValidationError(
                "INVALID_RACE_ANSWERS", "Race results require eight saved answers."
            )
        use_saved_answers = bool(saved_answers) or race.mode != "training"
        answer_count = len(saved_answers) if use_saved_answers else len(request.answers)
        if race.mode != "training":
            answer_count = 8
        try:
            if race.mode == "training":
                generated_problems = _generate_training_problems(
                    generate_problem_set,
                    race.difficulty_tier,
                    int(race.seed),
                    answer_count,
                    custom_tier_config,
                )
            else:
                generated_problems = generate_problem_set(
                    race.difficulty_tier, int(race.seed), 8, custom_tier_config
                ).problems
        except (KeyError, ValueError) as error:
            raise ValidationError(
                "RACE_TIER_UNAVAILABLE",
                "Race settings are not available for result validation.",
            ) from error

        validated_answers: list[OperationAnswerRequest] = []
        for index, problem in enumerate(generated_problems):
            if use_saved_answers:
                saved = saved_answers[index]
                operation = saved.operation
                submitted_answer = saved.submitted_answer or ""
                response_time_ms = saved.response_time_ms
                is_correct = saved.is_correct
            else:
                answer = request.answers[index]
                operation = answer.operation
                submitted_answer = answer.answer
                response_time_ms = answer.response_time_ms or 0
                try:
                    is_correct = int(answer.answer.strip()) == problem.answer
                except ValueError:
                    is_correct = False
            if operation != problem.operation.value:
                raise ValidationError(
                    "INVALID_RACE_ANSWERS",
                    "Answer operations do not match the stored race questions.",
                )
            if use_saved_answers:
                try:
                    is_correct = int(submitted_answer.strip()) == problem.answer
                except ValueError:
                    is_correct = False
                if is_correct != saved_answers[index].is_correct:
                    raise ValidationError(
                        "INVALID_RACE_ANSWERS",
                        "Saved answer correctness does not match the race question.",
                    )
            validated_answers.append(
                OperationAnswerRequest(
                    operation=operation,
                    is_correct=is_correct,
                    response_time_ms=response_time_ms,
                    submitted_answer=submitted_answer,
                )
            )

        correct_answers = sum(answer.is_correct for answer in validated_answers)
        current_streak = 0
        longest_streak = 0
        total_distance = 0
        for validated_answer in validated_answers:
            if validated_answer.is_correct:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
                if validated_answer.response_time_ms < 2000:
                    total_distance += 18
                elif validated_answer.response_time_ms < 4000:
                    total_distance += 15
                elif validated_answer.response_time_ms < 6000:
                    total_distance += 12
                else:
                    total_distance += 9
            else:
                current_streak = 0
        average_response_ms = (
            (
                sum(answer.response_time_ms for answer in validated_answers)
                + len(validated_answers) // 2
            )
            // len(validated_answers)
            if validated_answers
            else 0
        )
        if race.mode != "training" and (correct_answers > 8 or total_distance > 144):
            raise ValidationError("INVALID_RACE_RESULT", "Race result exceeds the track limits.")
        if race.mode != "training":
            ai_participants = simulate_opponents(int(race.seed), race.opponent_count or 0)
            all_results = [
                *ai_participants,
                OpponentResult(
                    avatar_id=request.human_avatar_id,
                    runner_id="player",
                    problems_correct=correct_answers,
                    longest_streak=longest_streak,
                    average_response_ms=average_response_ms,
                    total_distance=total_distance,
                ),
            ]
            ranked = sorted(
                all_results,
                key=lambda participant: (
                    -participant.total_distance,
                    participant.runner_id,
                ),
            )
            position_by_avatar = {
                participant.avatar_id: index + 1 for index, participant in enumerate(ranked)
            }
            if any(
                participant.position != position_by_avatar[participant.avatar_id]
                for participant in request.participants
            ):
                raise ValidationError(
                    "INVALID_RACE_RESULT", "Participant positions do not match the race outcome."
                )
            computed_participants = []
            for participant in all_results:
                computed_participants.append(
                    ParticipantSummaryRequest(
                        avatar_id=participant.avatar_id,
                        position=position_by_avatar[participant.avatar_id],
                        problems_correct=participant.problems_correct,
                        longest_streak=participant.longest_streak,
                        average_response_ms=participant.average_response_ms,
                        total_distance=participant.total_distance,
                        xp_earned=0,
                    )
                )
        else:
            computed_participants = [
                ParticipantSummaryRequest(
                    avatar_id=request.human_avatar_id,
                    position=None,
                    problems_correct=correct_answers,
                    longest_streak=longest_streak,
                    average_response_ms=average_response_ms,
                    total_distance=total_distance,
                    xp_earned=0,
                )
            ]
        summary = RaceSummaryRequest(
            human_avatar_id=request.human_avatar_id,
            race_id=race.id,
            idempotency_key=request.idempotency_key,
            seed=race.seed,
            difficulty_tier=race.difficulty_tier,
            mode=race.mode,
            child_profile_id=child_profile_id,
            started_at=race.started_at,
            completed_at=datetime.now(UTC),
            participants=computed_participants,
            answers=validated_answers,
        )
        response = await self.persist_race(summary, account_id=account_id, session=session)
        await self._repository.save_result_response(
            race.id,
            payload,
            response.model_dump(mode="json"),
        )
        return response

    async def persist_race(
        self,
        request: RaceSummaryRequest,
        account_id: uuid.UUID | None = None,
        session: AsyncSession | None = None,
    ) -> RaceSummaryResponse:
        positions = [p.position for p in request.participants]
        if len(positions) != len(set(positions)):
            raise ValidationError(message="Participant positions must be unique within a race.")

        player = next(
            (p for p in request.participants if p.avatar_id == request.human_avatar_id),
            None,
        )
        if account_id is not None and player is None:
            raise ValidationError(message="Human avatar is not a race participant.")

        progression = None
        if account_id is not None and self._progression_repository is not None:
            from app.progression.domain_service import ProgressionDomainService

            assert player is not None
            prog_service = ProgressionDomainService(self._progression_repository)
            progression = await prog_service.award_xp(
                account_id=account_id,
                problems_correct=player.problems_correct,
                longest_streak=player.longest_streak,
                mode=request.mode,
                race_id=request.race_id,
                child_profile_id=request.child_profile_id,
            )
            xp_earned = progression.xp_earned_this_race
            if xp_earned is None:
                raise RuntimeError("XP award did not return an earned amount.")
            player.xp_earned = xp_earned

        response = await self._repository.create(request)
        response.progression = progression

        if player is not None and account_id is not None and progression is not None:
            if self._achievement_repository is not None and session is not None:
                from app.achievements.domain_service import AchievementDomainService

                ach_service = AchievementDomainService(self._achievement_repository)
                event_data = {
                    "problems_correct": player.problems_correct,
                    "position": player.position,
                    "average_response_ms": player.average_response_ms,
                    "mode": request.mode,
                }
                new_achievements = await ach_service.evaluate_race_completed(
                    account_id, event_data, session, request.child_profile_id
                )
                if progression.level_up is not None:
                    new_achievements += await ach_service.evaluate_level_up(
                        account_id,
                        progression.level_up.new_level,
                        session,
                        request.child_profile_id,
                    )
                response.new_achievements = new_achievements

        if account_id is not None and self._statistics_service is not None:
            await self._statistics_service.update_on_race(account_id, request)

        return response
