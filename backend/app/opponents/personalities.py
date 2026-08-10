from __future__ import annotations

from app.opponents.schemas import PersonalityDefinitionResponse

PERSONALITIES: list[PersonalityDefinitionResponse] = [
    PersonalityDefinitionResponse(
        id="steady",
        name="Steady",
        accuracy_rate=0.80,
        base_response_time_ms=3500,
        response_time_variance_ms=175,
        speed_profile="uniform",
        tier_offset=0,
    ),
    PersonalityDefinitionResponse(
        id="speedster",
        name="Speedster",
        accuracy_rate=0.70,
        base_response_time_ms=3500,
        response_time_variance_ms=350,
        speed_profile="front_loaded",
        tier_offset=1,
    ),
    PersonalityDefinitionResponse(
        id="slow_starter",
        name="Slow Starter",
        accuracy_rate=0.75,
        base_response_time_ms=3500,
        response_time_variance_ms=280,
        speed_profile="back_loaded",
        tier_offset=0,
    ),
    PersonalityDefinitionResponse(
        id="unpredictable",
        name="Unpredictable",
        accuracy_rate=0.65,
        base_response_time_ms=3500,
        response_time_variance_ms=875,
        speed_profile="random",
        tier_offset=0,
    ),
    PersonalityDefinitionResponse(
        id="balanced",
        name="Balanced",
        accuracy_rate=0.78,
        base_response_time_ms=3500,
        response_time_variance_ms=245,
        speed_profile="uniform",
        tier_offset=0,
    ),
]
