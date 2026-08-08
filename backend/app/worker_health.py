"""Health probe for the worker container.

Checks Redis connectivity. Exits 0 if healthy, 1 if not.
Used by the Docker Compose worker health check.
"""

import asyncio
import sys


async def check() -> None:
    from infrastructure.config import get_config
    import redis.asyncio as aioredis

    cfg = get_config()
    try:
        client = aioredis.from_url(cfg.REDIS_URL)
        await client.ping()
        await client.aclose()
        sys.exit(0)
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(check())
