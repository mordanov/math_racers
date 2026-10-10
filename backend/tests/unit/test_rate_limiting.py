from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from infrastructure.rate_limiting import RedisRateLimiter

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_rate_limiter_allows_requests_within_limit() -> None:
    client = AsyncMock()
    client.eval.return_value = 3

    await RedisRateLimiter(client).enforce("login:key", limit=5, window_seconds=60)

    client.eval.assert_awaited_once()


@pytest.mark.asyncio
async def test_rate_limiter_rejects_requests_over_limit() -> None:
    client = AsyncMock()
    client.eval.return_value = 6

    with pytest.raises(HTTPException) as exc_info:
        await RedisRateLimiter(client).enforce("login:key", limit=5, window_seconds=60)

    assert exc_info.value.status_code == 429
    assert exc_info.value.headers == {"Retry-After": "60"}


@pytest.mark.asyncio
async def test_rate_limiter_reports_redis_unavailable() -> None:
    from redis.exceptions import RedisError

    client = AsyncMock()
    client.eval.side_effect = RedisError("unavailable")

    with pytest.raises(HTTPException) as exc_info:
        await RedisRateLimiter(client).enforce("login:key", limit=5, window_seconds=60)

    assert exc_info.value.status_code == 503
