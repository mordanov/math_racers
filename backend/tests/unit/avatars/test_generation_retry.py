"""Unit tests — generation_service retry backoff."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.avatars.generation_service import _backoff_seconds


@pytest.mark.unit
def test_backoff_after_first_failed_attempt_is_30s() -> None:
    assert _backoff_seconds(1) == 30


@pytest.mark.unit
def test_backoff_after_second_failed_attempt_is_120s() -> None:
    assert _backoff_seconds(2) == 120


@pytest.mark.unit
def test_backoff_after_third_or_more_failed_attempts_is_480s() -> None:
    assert _backoff_seconds(3) == 480
    assert _backoff_seconds(4) == 480
    assert _backoff_seconds(10) == 480


def _make_mock_session(mock_repo: AsyncMock) -> tuple[MagicMock, MagicMock]:
    """Return (mock_session_instance, mock_session_class) wired for async context managers."""
    mock_begin = MagicMock()
    mock_begin.__aenter__ = AsyncMock(return_value=mock_begin)
    mock_begin.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    mock_session.begin = MagicMock(return_value=mock_begin)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_cls = MagicMock(return_value=mock_session)
    return mock_session, mock_cls


@pytest.mark.unit
@pytest.mark.asyncio
async def test_run_generation_job_skips_complete_jobs() -> None:
    job_id = uuid.uuid4()
    mock_job = MagicMock()
    mock_job.status = "complete"

    mock_repo = AsyncMock()
    mock_repo.get_job.return_value = mock_job
    _, mock_session_cls = _make_mock_session(mock_repo)

    with (
        patch("app.avatars.generation_service.get_config"),
        patch("app.avatars.repository.SQLAlchemyAvatarRepository", return_value=mock_repo),
        patch("sqlalchemy.ext.asyncio.create_async_engine"),
        patch("sqlalchemy.ext.asyncio.AsyncSession", mock_session_cls),
        patch("app.avatars.generation_service._run_pipeline") as mock_pipeline,
    ):
        from app.avatars.generation_service import run_generation_job

        await run_generation_job(job_id)
        mock_pipeline.assert_not_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_run_generation_job_processes_retrying_jobs() -> None:
    job_id = uuid.uuid4()
    mock_job = MagicMock()
    mock_job.status = "retrying"
    mock_avatar = MagicMock()

    mock_repo = AsyncMock()
    mock_repo.get_job.return_value = mock_job
    mock_repo.get.return_value = mock_avatar
    _, mock_session_cls = _make_mock_session(mock_repo)

    mock_engine = AsyncMock()
    with (
        patch("app.avatars.generation_service.get_config"),
        patch("app.avatars.repository.SQLAlchemyAvatarRepository", return_value=mock_repo),
        patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=mock_engine),
        patch("sqlalchemy.ext.asyncio.AsyncSession", mock_session_cls),
        patch("app.avatars.generation_service._run_pipeline") as mock_pipeline,
    ):
        mock_pipeline.return_value = None
        from app.avatars.generation_service import run_generation_job

        await run_generation_job(job_id)
        mock_pipeline.assert_called_once()
