from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from math import floor

_MASK = 0xFFFFFFFF
_PERSONALITIES = (
    (0.8, "uniform"),
    (0.7, "front_loaded"),
    (0.75, "back_loaded"),
    (0.65, "random"),
    (0.78, "uniform"),
)


@dataclass(frozen=True)
class OpponentResult:
    avatar_id: str
    runner_id: str
    problems_correct: int
    longest_streak: int
    average_response_ms: int
    total_distance: int


def _create_rng(seed: int) -> Callable[[], float]:
    state = seed & _MASK

    def next_value() -> float:
        nonlocal state
        state = (state + 0x6D2B79F5) & _MASK
        value = state
        value = ((value ^ (value >> 15)) * (value | 1)) & _MASK
        value ^= (value + (((value ^ (value >> 7)) * (value | 61)) & _MASK)) & _MASK
        value = (value ^ (value >> 14)) & _MASK
        return value / 0x100000000

    return next_value


def _simulate_opponent(
    seed: int, opponent_index: int, accuracy: float, profile: str
) -> OpponentResult:
    rng = _create_rng(seed + opponent_index + 1)
    is_correct_results: list[bool] = []
    response_times: list[float] = []

    for checkpoint_index in range(8):
        accuracy_roll = rng()
        is_correct_results.append(accuracy_roll < accuracy)

        t = checkpoint_index / 7
        if profile == "front_loaded":
            base = 1500 + (5000 - 1500) * t
        elif profile == "back_loaded":
            base = 5000 + (1500 - 5000) * t
        elif profile == "random":
            base = rng() * 6000 + 1000
        else:
            base = 3500
        base += (rng() - 0.5) * 1000

        if profile == "front_loaded":
            multiplier = 1.2 if checkpoint_index < 3 else 1.0 if checkpoint_index < 6 else 0.9
        elif profile == "back_loaded":
            multiplier = 0.85 if checkpoint_index < 3 else 1.0 if checkpoint_index < 6 else 1.25
        elif profile == "random":
            multiplier = 0.7 + rng() * 0.6
        else:
            multiplier = 1.0
        response_times.append(max(0.0, base * multiplier))

    distances = [
        (
            (
                18
                if response_time < 2000
                else 15 if response_time < 4000 else 12 if response_time < 6000 else 9
            )
            if is_correct
            else 0
        )
        for is_correct, response_time in zip(is_correct_results, response_times, strict=True)
    ]
    longest_streak = 0
    current_streak = 0
    for is_correct in is_correct_results:
        if is_correct:
            current_streak += 1
            longest_streak = max(longest_streak, current_streak)
        else:
            current_streak = 0

    return OpponentResult(
        avatar_id=f"ai-{opponent_index}",
        runner_id=f"ai-{opponent_index}",
        problems_correct=sum(is_correct_results),
        longest_streak=longest_streak,
        average_response_ms=floor(sum(response_times) / len(response_times) + 0.5),
        total_distance=sum(distances),
    )


def simulate_opponents(seed: int, opponent_count: int) -> list[OpponentResult]:
    return [
        _simulate_opponent(seed, index, *_PERSONALITIES[(index - 1) % len(_PERSONALITIES)])
        for index in range(1, opponent_count + 1)
    ]
