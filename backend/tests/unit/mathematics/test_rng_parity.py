"""Parity smoke-test: Python Mulberry32 produces values in [0, 1)."""

from __future__ import annotations

from app.mathematics.rng import create_rng


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
