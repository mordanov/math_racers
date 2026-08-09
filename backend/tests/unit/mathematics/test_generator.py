"""Unit tests for the mathematics problem generator."""

from __future__ import annotations

from app.mathematics.generator import generate_problem_set
from app.mathematics.types import Operation


def test_determinism_same_seed_same_output() -> None:
    a = generate_problem_set(2, 1234567890, 8)
    b = generate_problem_set(2, 1234567890, 8)
    for pa, pb in zip(a.problems, b.problems):
        assert pa.operation == pb.operation
        assert pa.operand_a == pb.operand_a
        assert pa.operand_b == pb.operand_b
        assert pa.answer == pb.answer


def test_determinism_different_seed_different_output() -> None:
    a = generate_problem_set(2, 1234567890, 20)
    b = generate_problem_set(2, 9999999999, 20)
    all_same = all(
        pa.operation == pb.operation
        and pa.operand_a == pb.operand_a
        and pa.operand_b == pb.operand_b
        for pa, pb in zip(a.problems, b.problems)
    )
    assert not all_same


def test_count_zero_returns_empty_set() -> None:
    result = generate_problem_set(1, 42, 0)
    assert len(result.problems) == 0
    assert result.count == 0


def test_tier1_only_addition() -> None:
    result = generate_problem_set(1, 7, 100)
    assert all(p.operation == Operation.addition for p in result.problems)


def test_tier1_operands_in_range() -> None:
    result = generate_problem_set(1, 7, 100)
    for p in result.problems:
        assert 1 <= p.operand_a <= 10
        assert 1 <= p.operand_b <= 10


def test_tier4_all_four_operations_present() -> None:
    result = generate_problem_set(4, 333, 200)
    ops = {p.operation for p in result.problems}
    assert Operation.addition in ops
    assert Operation.subtraction in ops
    assert Operation.multiplication in ops
    assert Operation.division in ops


def test_division_integer_answers() -> None:
    result = generate_problem_set(4, 99, 200)
    divisions = [p for p in result.problems if p.operation == Operation.division]
    assert len(divisions) > 0
    for p in divisions:
        assert p.operand_b != 0
        assert p.operand_a % p.operand_b == 0
        assert p.answer == p.operand_a // p.operand_b


def test_subtraction_non_negative_results() -> None:
    result = generate_problem_set(2, 55, 200)
    subtractions = [p for p in result.problems if p.operation == Operation.subtraction]
    assert len(subtractions) > 0
    for p in subtractions:
        assert p.operand_a >= p.operand_b
        assert p.answer >= 0


def test_no_consecutive_duplicates() -> None:
    result = generate_problem_set(1, 12345, 200)
    for i in range(1, len(result.problems)):
        prev = result.problems[i - 1]
        curr = result.problems[i]
        identical = (
            curr.operation == prev.operation
            and curr.operand_a == prev.operand_a
            and curr.operand_b == prev.operand_b
        )
        assert not identical


def test_tier6_fallback_uses_tier5_range() -> None:
    result = generate_problem_set(6, 1, 50)
    for p in result.problems:
        assert 1 <= p.operand_a <= 100
        assert 1 <= p.operand_b <= 100
    assert result.tier == 6
