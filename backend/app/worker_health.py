"""Health probe for the worker container.

Checks Redis connectivity. Exits 0 if healthy, 1 if not.
Used by the Docker Compose worker health check.
"""

import asyncio
import sys


async def check() -> None:
    import redis.asyncio as aioredis

    from infrastructure.config import get_config

    cfg = get_config()
    try:
        client = aioredis.from_url(cfg.REDIS_URL)  # type: ignore[no-untyped-call]
        await client.ping()
        await client.aclose()
        sys.exit(0)
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(check())
