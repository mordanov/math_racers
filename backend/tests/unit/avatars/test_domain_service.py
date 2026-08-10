"""Unit tests for AvatarDomainService create path (mocked repository and Redis)."""
from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.avatars.domain_service import AvatarDomainService
from app.avatars.schemas import CreateAvatarRequest
from app.shared.exceptions import ValidationError

_ACCOUNT_ID = uuid.uuid4()


def _make_avatar(account_id: uuid.UUID = _ACCOUNT_ID) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        account_id=account_id,
        species="fox",
        fur_color="#FF6600",
        eye_color="#00AAFF",
        hairstyle="spiky",
        accessories=[],
        clothes_top_color="#4169E1",
        clothes_bottom_color="#FFFFFF",
        name=None,
        personality=None,
        biography=None,
        appearance_summary=None,
        favorite_subject=None,
        running_style=None,
        status="pending",
        is_favourite=False,
        active_portrait_id=None,
        active_portrait=None,
        portraits=[],
        generation_jobs=[],
        created_at="2025-01-01T00:00:00Z",
    )


def _make_job(avatar_id: uuid.UUID) -> SimpleNamespace:
    return SimpleNamespace(id=uuid.uuid4(), avatar_id=avatar_id, status="queued")


def _make_repo(avatar: SimpleNamespace, job: SimpleNamespace) -> MagicMock:
    repo = MagicMock()
    repo.count_by_account = AsyncMock(return_value=0)
    repo.count_active_jobs_by_account = AsyncMock(return_value=0)
    repo.count_jobs_last_hour_by_account = AsyncMock(return_value=0)
    repo.create = AsyncMock(return_value=avatar)
    repo.create_job = AsyncMock(return_value=job)
    return repo


_REQUEST = CreateAvatarRequest(
    species="fox",
    fur_color="#FF6600",
    eye_color="#00AAFF",
    hairstyle="spiky",
)


@pytest.mark.asyncio
async def test_create_returns_response():
    avatar = _make_avatar()
    job = _make_job(avatar.id)
    repo = _make_repo(avatar, job)

    with patch("app.avatars.domain_service._enqueue_job"):
        service = AvatarDomainService(repo, "redis://localhost")
        result = await service.create(_ACCOUNT_ID, _REQUEST)

    assert result.avatar_id == avatar.id
    assert result.job_id == job.id
    assert result.status == "queued"


@pytest.mark.asyncio
async def test_create_enqueues_job():
    avatar = _make_avatar()
    job = _make_job(avatar.id)
    repo = _make_repo(avatar, job)

    with patch("app.avatars.domain_service._enqueue_job") as mock_enqueue:
        service = AvatarDomainService(repo, "redis://localhost")
        await service.create(_ACCOUNT_ID, _REQUEST)

    mock_enqueue.assert_called_once_with("redis://localhost", job.id, avatar.id)


@pytest.mark.asyncio
async def test_create_raises_when_avatar_limit_reached():
    avatar = _make_avatar()
    job = _make_job(avatar.id)
    repo = _make_repo(avatar, job)
    repo.count_by_account = AsyncMock(return_value=50)

    service = AvatarDomainService(repo, "redis://localhost")
    with pytest.raises(ValidationError) as exc_info:
        await service.create(_ACCOUNT_ID, _REQUEST)

    assert exc_info.value.error_code == "AVATAR_LIMIT_REACHED"


@pytest.mark.asyncio
async def test_create_raises_when_concurrency_limit_reached():
    avatar = _make_avatar()
    job = _make_job(avatar.id)
    repo = _make_repo(avatar, job)
    repo.count_active_jobs_by_account = AsyncMock(return_value=2)

    service = AvatarDomainService(repo, "redis://localhost")
    with pytest.raises(ValidationError) as exc_info:
        await service.create(_ACCOUNT_ID, _REQUEST)

    assert exc_info.value.error_code == "CONCURRENCY_LIMIT_REACHED"


@pytest.mark.asyncio
async def test_create_raises_when_rate_limit_exceeded():
    avatar = _make_avatar()
    job = _make_job(avatar.id)
    repo = _make_repo(avatar, job)
    repo.count_jobs_last_hour_by_account = AsyncMock(return_value=10)

    service = AvatarDomainService(repo, "redis://localhost")
    with pytest.raises(ValidationError) as exc_info:
        await service.create(_ACCOUNT_ID, _REQUEST)

    assert exc_info.value.error_code == "RATE_LIMIT_EXCEEDED"
