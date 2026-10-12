from __future__ import annotations

import logging
import uuid
from collections.abc import Generator

from app.mathematics.rng import create_rng
from app.mathematics.tiers import TIER_CONFIGS, TierConfig, supports_division
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
        if config.tier in (4, 5):
            min_divisor = max(2, lo)
            max_divisor = min(9, hi // 2)
        else:
            min_divisor = max(2, lo)
            max_divisor = hi // 2
        b = _random_int(rng, min_divisor, max_divisor)
        a = b * _random_int(rng, 2, hi // b)
        return a, b
    if operation == Operation.subtraction:
        a = _random_int(rng, lo, hi)
        b = _random_int(rng, lo, a)
        return a, b
    if operation == Operation.addition and config.tier == 5:
        return _random_int(rng, 10, 99), _random_int(rng, 10, 99)
    if operation == Operation.multiplication and config.tier in (3, 5):
        return _random_int(rng, 10, 99), _random_int(rng, 1, 9)
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
        if custom_tier_config is None:
            raise ValueError("Tier 6 requires parent-configured settings.")
        config = custom_tier_config
    else:
        config = TIER_CONFIGS[tier]
    if Operation.division in config.operations and not supports_division(
        config.min_operand, config.max_operand
    ):
        raise ValueError("The operand range cannot generate a division quotient above one.")

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
                        extra={
                            "context": {
                                "tier": tier,
                                "seed": seed,
                                "slot": len(problems),
                            }
                        },
                    )
                problem = candidate
                break
        problems.append(problem)  # type: ignore[arg-type]
        last = problem

    return ProblemSet(seed=seed, tier=tier, count=count, problems=tuple(problems))
