from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from app.mathematics.generator import generate_problem_set
from app.mathematics.schemas import ProblemResponse, ProblemSetResponse

router = APIRouter(prefix="/api/v1", tags=["mathematics"])


@router.get("/problems", response_model=ProblemSetResponse)
async def get_problems(
    tier: Annotated[int, Query(ge=1, le=6)],
    seed: Annotated[int, Query(ge=0, le=4294967295)],
    count: Annotated[int, Query(ge=0, le=100)],
) -> ProblemSetResponse:
    problem_set = generate_problem_set(tier, seed, count)
    return ProblemSetResponse(
        seed=problem_set.seed,
        tier=problem_set.tier,
        count=problem_set.count,
        problems=[
            ProblemResponse(
                id=p.id,
                operation=p.operation,
                operand_a=p.operand_a,
                operand_b=p.operand_b,
                answer=p.answer,
                tier=p.tier,
                seed=p.seed,
            )
            for p in problem_set.problems
        ],
    )
