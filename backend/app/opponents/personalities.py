from __future__ import annotations

from app.opponents.schemas import PersonalityDefinitionResponse

PERSONALITIES: list[PersonalityDefinitionResponse] = [
    PersonalityDefinitionResponse(
        id="steady",
        name="Steady",
        accuracyRate=0.80,
        baseResponseTimeMs=3500,
        responseTimeVarianceMs=175,
        speedProfile="uniform",
        tierOffset=0,
    ),
    PersonalityDefinitionResponse(
        id="speedster",
        name="Speedster",
        accuracyRate=0.70,
        baseResponseTimeMs=3500,
        responseTimeVarianceMs=350,
        speedProfile="front_loaded",
        tierOffset=1,
    ),
    PersonalityDefinitionResponse(
        id="slow_starter",
        name="Slow Starter",
        accuracyRate=0.75,
        baseResponseTimeMs=3500,
        responseTimeVarianceMs=280,
        speedProfile="back_loaded",
        tierOffset=0,
    ),
    PersonalityDefinitionResponse(
        id="unpredictable",
        name="Unpredictable",
        accuracyRate=0.65,
        baseResponseTimeMs=3500,
        responseTimeVarianceMs=875,
        speedProfile="random",
        tierOffset=0,
    ),
    PersonalityDefinitionResponse(
        id="balanced",
        name="Balanced",
        accuracyRate=0.78,
        baseResponseTimeMs=3500,
        responseTimeVarianceMs=245,
        speedProfile="uniform",
        tierOffset=0,
    ),
]
