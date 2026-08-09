from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import StrEnum


class Operation(StrEnum):
    addition = "addition"
    subtraction = "subtraction"
    multiplication = "multiplication"
    division = "division"


@dataclass(frozen=True)
class Problem:
    id: uuid.UUID
    operation: Operation
    operand_a: int
    operand_b: int
    answer: int
    tier: int
    seed: int


@dataclass(frozen=True)
class ProblemSet:
    seed: int
    tier: int
    count: int
    problems: tuple[Problem, ...]
