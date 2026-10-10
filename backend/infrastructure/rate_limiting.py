from __future__ import annotations

from typing import Protocol

from redis.exceptions import RedisError


class RedisClient(Protocol):
    async def eval(self, script: str, numkeys: int, *keys_and_args: str) -> int | str: ...
    async def aclose(self) -> None: ...


_INCREMENT_WITH_TTL = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return count
"""


class RedisRateLimiter:
    def __init__(self, client: RedisClient) -> None:
        self._client = client

    async def close(self) -> None:
        await self._client.aclose()

    async def enforce(self, key: str, limit: int, window_seconds: int) -> None:
        from fastapi import HTTPException

        try:
            count = await self._client.eval(
                _INCREMENT_WITH_TTL,
                1,
                key,
                str(window_seconds),
            )
        except RedisError as exc:
            raise HTTPException(
                status_code=503,
                detail="Rate limiting is unavailable. Try again later.",
            ) from exc

        if int(count) > limit:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Try again later.",
                headers={"Retry-After": str(window_seconds)},
            )
