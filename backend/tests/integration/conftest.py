from __future__ import annotations

import os

import pytest
from redis import Redis


@pytest.fixture(autouse=True)
def clear_isolated_rate_limits() -> None:
    if os.getenv("INTEGRATION_TESTING") != "1":
        return

    database_url = os.getenv("DATABASE_URL", "")
    redis_url = os.getenv("REDIS_URL", "")
    if "mathracers_test" not in database_url or not redis_url:
        raise RuntimeError("Integration rate-limit cleanup requires an isolated test database.")

    client = Redis.from_url(redis_url)
    try:
        keys = [
            *client.scan_iter(match="auth:*"),
            *client.scan_iter(match="avatar:generation:*"),
        ]
        if keys:
            client.delete(*keys)
    finally:
        client.connection_pool.disconnect()
