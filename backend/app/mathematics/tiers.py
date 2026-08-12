from __future__ import annotations

from dataclasses import dataclass

from app.mathematics.types import Operation


@dataclass(frozen=True)
class TierConfig:
    tier: int
    operations: tuple[Operation, ...]
    min_operand: int
    max_operand: int


TIER_CONFIGS: dict[int, TierConfig] = {
    1: TierConfig(1, (Operation.addition,), 1, 10),
    2: TierConfig(2, (Operation.addition, Operation.subtraction), 1, 20),
    3: TierConfig(
        3, (Operation.addition, Operation.subtraction, Operation.multiplication), 1, 12
    ),
    4: TierConfig(
        4,
        (
            Operation.addition,
            Operation.subtraction,
            Operation.multiplication,
            Operation.division,
        ),
        1,
        25,
    ),
    5: TierConfig(
        5,
        (
            Operation.addition,
            Operation.subtraction,
            Operation.multiplication,
            Operation.division,
        ),
        1,
        100,
    ),
}
