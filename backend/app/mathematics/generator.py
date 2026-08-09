from __future__ import annotations

import logging
import uuid
from collections.abc import Generator

from app.mathematics.rng import create_rng
from app.mathematics.tiers import TIER_CONFIGS, TierConfig
from app.mathematics.types import Operation, Problem, ProblemSet

logger = logging.getLogger(__name__)

_MAX_RETRIES = 10


def _random_int(rng: Generator[float, None, None], lo: int, hi: int) -> int:
    return int(next(rng) * (hi - lo + 1)) + lo


def _pick_operation(config: TierConfig, rng: Generator[float, None, None]) -> Operation:
    ops = config.operations
    return ops[int(next(rng) * len(ops))]


def _pick_operands(
    operation: Operation, config: TierConfig, rng: Generator[float, None, None]
) -> tuple[int, int]:
    lo, hi = config.min_operand, config.max_operand
    if operation == Operation.division:
        b = _random_int(rng, 2, hi)
        max_multiplier = max(1, hi // b)
        a = b * _random_int(rng, 1, max_multiplier)
        return a, b
    if operation == Operation.subtraction:
        a = _random_int(rng, lo, hi)
        b = _random_int(rng, lo, a)
        return a, b
    return _random_int(rng, lo, hi), _random_int(rng, lo, hi)


def _compute(operation: Operation, a: int, b: int) -> int:
    if operation == Operation.addition:
        return a + b
    if operation == Operation.subtraction:
        return a - b
    if operation == Operation.multiplication:
        return a * b
    return a // b


def _is_duplicate(candidate: Problem, last: Problem | None) -> bool:
    if last is None:
        return False
    return (
        candidate.operation == last.operation
        and candidate.operand_a == last.operand_a
        and candidate.operand_b == last.operand_b
    )


def generate_problem_set(
    tier: int,
    seed: int,
    count: int,
    custom_tier_config: TierConfig | None = None,
) -> ProblemSet:
    if tier == 6:
        config = custom_tier_config or TierConfig(
            6,
            TIER_CONFIGS[5].operations,
            TIER_CONFIGS[5].min_operand,
            TIER_CONFIGS[5].max_operand,
        )
    else:
        config = TIER_CONFIGS[tier]

    rng = create_rng(seed)
    problems: list[Problem] = []
    last: Problem | None = None

    while len(problems) < count:
        problem: Problem | None = None
        for attempt in range(_MAX_RETRIES + 1):
            operation = _pick_operation(config, rng)
            a, b = _pick_operands(operation, config, rng)
            answer = _compute(operation, a, b)
            candidate = Problem(
                id=uuid.uuid4(),
                operation=operation,
                operand_a=a,
                operand_b=b,
                answer=answer,
                tier=tier,
                seed=seed,
            )
            if not _is_duplicate(candidate, last) or attempt == _MAX_RETRIES:
                if attempt == _MAX_RETRIES and _is_duplicate(candidate, last):
                    logger.warning(
                        "Retry limit reached — accepting duplicate problem",
                        extra={"context": {"tier": tier, "seed": seed, "slot": len(problems)}},
                    )
                problem = candidate
                break
        problems.append(problem)  # type: ignore[arg-type]
        last = problem

    return ProblemSet(seed=seed, tier=tier, count=count, problems=tuple(problems))
