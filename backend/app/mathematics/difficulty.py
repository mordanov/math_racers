from __future__ import annotations


def select_tier(current_tier: int, skill_score: float, parent_override: int | None = None) -> int:
    if parent_override is not None:
        return max(1, min(6, parent_override))
    if skill_score >= 0.90:
        return min(current_tier + 1, 6)
    if skill_score < 0.60:
        return max(current_tier - 1, 1)
    return current_tier
