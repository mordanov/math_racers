"""Unit tests — process_job correlation ID handling."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.unit
async def test_process_job_sets_request_id_before_dispatch() -> None:
    """process_job sets the request_id context var before calling the handler."""
    from app.worker import process_job

    job_rid = str(uuid.uuid4())
    job: dict[str, object] = {
        "job_type": "avatar_generation",
        "job_id": str(uuid.uuid4()),
        "avatar_id": str(uuid.uuid4()),
        "request_id": job_rid,
    }

    with (
        patch("app.worker.set_request_id") as mock_set_rid,
        patch(
            "app.avatars.generation_service.run_generation_job",
            new=AsyncMock(return_value=None),
        ),
    ):
        await process_job(job)

    mock_set_rid.assert_called_once_with(job_rid)


@pytest.mark.unit
async def test_process_job_tolerates_missing_request_id() -> None:
    """process_job does not raise when job payload has no request_id key."""
    from app.worker import process_job

    job: dict[str, object] = {
        "job_type": "avatar_generation",
        "job_id": str(uuid.uuid4()),
        "avatar_id": str(uuid.uuid4()),
        # no request_id key — simulates a job enqueued before this change
    }

    with patch(
        "app.avatars.generation_service.run_generation_job",
        new=AsyncMock(return_value=None),
    ):
        await process_job(job)  # must not raise


@pytest.mark.unit
async def test_process_job_resets_request_id_to_nil_for_legacy_jobs() -> None:
    """process_job resets request_id to the nil UUID when job has no request_id key."""
    from app.worker import process_job
    from infrastructure.logging import request_id_var

    # Simulate a previous job having set the ContextVar to a non-nil value.
    token = request_id_var.set("previous-job-uuid")
    try:
        job: dict[str, object] = {
            "job_type": "avatar_generation",
            "job_id": str(uuid.uuid4()),
            "avatar_id": str(uuid.uuid4()),
            # no request_id — legacy job enqueued before correlation ID support
        }
        with patch(
            "app.avatars.generation_service.run_generation_job",
            new=AsyncMock(return_value=None),
        ):
            await process_job(job)
        assert request_id_var.get() == "00000000-0000-0000-0000-000000000000"
    finally:
        request_id_var.reset(token)
