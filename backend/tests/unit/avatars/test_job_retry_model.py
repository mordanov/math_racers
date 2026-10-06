"""Unit tests — GenerationJob model includes retry states."""

from __future__ import annotations

import pytest

from app.avatars.models import GenerationJob


@pytest.mark.unit
def test_generation_job_status_constraint_includes_retrying() -> None:
    constraint = next(
        c
        for c in GenerationJob.__table_args__
        if hasattr(c, "name") and c.name == "ck_generation_jobs_status"
    )
    assert "'retrying'" in constraint.sqltext.text


@pytest.mark.unit
def test_generation_job_status_constraint_includes_permanent_failure() -> None:
    constraint = next(
        c
        for c in GenerationJob.__table_args__
        if hasattr(c, "name") and c.name == "ck_generation_jobs_status"
    )
    assert "'permanent_failure'" in constraint.sqltext.text
