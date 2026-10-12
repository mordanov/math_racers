"""Parity smoke-test: Python Mulberry32 produces values in [0, 1)."""

from __future__ import annotations

from app.mathematics.generator import generate_problem_set
from app.mathematics.rng import create_rng
from app.mathematics.tiers import TierConfig
from app.mathematics.types import Operation


def test_rng_values_in_unit_interval() -> None:
    rng = create_rng(1234567890)
    for _ in range(1000):
        v = next(rng)
        assert 0.0 <= v < 1.0


def test_rng_deterministic() -> None:
    a = create_rng(42)
    b = create_rng(42)
    for _ in range(50):
        assert next(a) == next(b)


def test_rng_different_seeds_differ() -> None:
    a = create_rng(1)
    b = create_rng(2)
    values_a = [next(a) for _ in range(20)]
    values_b = [next(b) for _ in range(20)]
    assert values_a != values_b


def test_problem_generator_matches_shared_seed_vectors() -> None:
    custom = TierConfig(
        tier=6,
        operations=(Operation.division,),
        min_operand=2,
        max_operand=30,
    )
    expected: dict[int, list[tuple[str, int, int]]] = {
        3: [
            ("multiplication", 37, 5),
            ("multiplication", 55, 4),
            ("multiplication", 78, 9),
            ("multiplication", 51, 9),
            ("multiplication", 97, 6),
            ("multiplication", 52, 3),
            ("multiplication", 87, 6),
            ("multiplication", 80, 6),
        ],
        4: [
            ("division", 16, 4),
            ("division", 18, 6),
            ("division", 24, 8),
            ("division", 25, 5),
            ("division", 18, 9),
            ("division", 15, 5),
            ("division", 24, 8),
            ("division", 10, 2),
        ],
        5: [
            ("division", 52, 4),
            ("division", 42, 6),
            ("addition", 78, 99),
            ("division", 95, 5),
            ("division", 72, 9),
            ("addition", 52, 37),
            ("division", 72, 8),
            ("subtraction", 8, 3),
        ],
        6: [
            ("division", 18, 6),
            ("division", 18, 9),
            ("division", 24, 12),
            ("division", 24, 8),
            ("division", 30, 15),
            ("division", 16, 8),
            ("division", 28, 14),
            ("division", 26, 13),
        ],
    }
    for tier in (3, 4, 5, 6):
        config = custom if tier == 6 else None
        problems = generate_problem_set(tier, 12345, 8, config).problems
        actual = [(p.operation.value, p.operand_a, p.operand_b) for p in problems]
        assert actual == expected[tier]
