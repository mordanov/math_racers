"""Unit tests for AvatarDomainService create path (mocked repository and Redis)."""

from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.avatars.domain_service import AvatarDomainService
from app.avatars.repository import SQLAlchemyAvatarRepository
from app.avatars.schemas import CreateAvatarRequest
from app.shared.exceptions import PermissionError, ValidationError

_ACCOUNT_ID = uuid.uuid4()


def _make_avatar(account_id: uuid.UUID = _ACCOUNT_ID) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        account_id=account_id,
        child_profile_id=uuid.uuid4(),
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
    repo.count_by_child = AsyncMock(return_value=0)
    repo.count_active_jobs_by_account = AsyncMock(return_value=0)
    repo.count_jobs_last_hour_by_account = AsyncMock(return_value=0)
    repo.lock_generation_quota = AsyncMock()
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
async def test_create_returns_response() -> None:
    avatar = _make_avatar()
    job = _make_job(avatar.id)
    repo = _make_repo(avatar, job)

    with patch("app.avatars.domain_service._enqueue_job"):
        service = AvatarDomainService(repo, "redis://localhost")
        result = await service.create(_ACCOUNT_ID, _REQUEST)

    assert result.avatar_id == avatar.id
    assert result.job_id == job.id
    assert result.status == "queued"
    repo.lock_generation_quota.assert_awaited_once_with(_ACCOUNT_ID)
    calls = [call[0] for call in repo.mock_calls]
    assert calls.index("lock_generation_quota") < calls.index("count_active_jobs_by_account")


@pytest.mark.asyncio
async def test_generation_quota_lock_is_scoped_to_account_and_transaction() -> None:
    session = MagicMock()
    session.execute = AsyncMock()

    await SQLAlchemyAvatarRepository(session).lock_generation_quota(_ACCOUNT_ID)

    statement = str(session.execute.await_args.args[0])
    assert "pg_advisory_xact_lock(hashtextextended(:account_id, 0))" in statement
    assert session.execute.await_args.args[1] == {"account_id": str(_ACCOUNT_ID)}


@pytest.mark.asyncio
async def test_create_enqueues_job() -> None:
    avatar = _make_avatar()
    job = _make_job(avatar.id)
    repo = _make_repo(avatar, job)

    with patch("app.avatars.domain_service._enqueue_job") as mock_enqueue:
        service = AvatarDomainService(repo, "redis://localhost")
        await service.create(_ACCOUNT_ID, _REQUEST)

    mock_enqueue.assert_called_once_with("redis://localhost", job.id, avatar.id)


@pytest.mark.asyncio
async def test_create_assigns_avatar_to_the_selected_child() -> None:
    avatar = _make_avatar()
    job = _make_job(avatar.id)
    repo = _make_repo(avatar, job)
    child_profile_id = uuid.uuid4()

    with patch("app.avatars.domain_service._enqueue_job"):
        service = AvatarDomainService(repo, "redis://localhost")
        await service.create(_ACCOUNT_ID, _REQUEST, child_profile_id)

    assert repo.create.await_args is not None
    assert repo.create.await_args.args[2] == child_profile_id


@pytest.mark.asyncio
async def test_create_raises_when_avatar_limit_reached() -> None:
    avatar = _make_avatar()
    job = _make_job(avatar.id)
    repo = _make_repo(avatar, job)
    repo.count_by_account = AsyncMock(return_value=50)

    service = AvatarDomainService(repo, "redis://localhost")
    with pytest.raises(ValidationError) as exc_info:
        await service.create(_ACCOUNT_ID, _REQUEST)

    assert exc_info.value.error_code == "AVATAR_LIMIT_REACHED"


@pytest.mark.asyncio
async def test_create_raises_when_concurrency_limit_reached() -> None:
    avatar = _make_avatar()
    job = _make_job(avatar.id)
    repo = _make_repo(avatar, job)
    repo.count_active_jobs_by_account = AsyncMock(return_value=2)

    service = AvatarDomainService(repo, "redis://localhost")
    with pytest.raises(ValidationError) as exc_info:
        await service.create(_ACCOUNT_ID, _REQUEST)

    assert exc_info.value.error_code == "CONCURRENCY_LIMIT_REACHED"


@pytest.mark.asyncio
async def test_create_raises_when_rate_limit_exceeded() -> None:
    avatar = _make_avatar()
    job = _make_job(avatar.id)
    repo = _make_repo(avatar, job)
    repo.count_jobs_last_hour_by_account = AsyncMock(return_value=10)

    service = AvatarDomainService(repo, "redis://localhost")
    with pytest.raises(ValidationError) as exc_info:
        await service.create(_ACCOUNT_ID, _REQUEST)

    assert exc_info.value.error_code == "RATE_LIMIT_EXCEEDED"


@pytest.mark.asyncio
async def test_get_rejects_avatar_owned_by_another_child() -> None:
    avatar = _make_avatar()
    repo = _make_repo(avatar, _make_job(avatar.id))
    repo.get = AsyncMock(return_value=avatar)
    service = AvatarDomainService(repo, "redis://localhost")

    with pytest.raises(PermissionError):
        await service.get(_ACCOUNT_ID, avatar.id, uuid.uuid4())
