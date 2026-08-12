"""Background worker — processes jobs from the Redis queue."""

import asyncio
import json
import signal
from typing import Any

from infrastructure.config import get_config
from infrastructure.logging import get_logger, setup_logging

logger = get_logger(__name__)

QUEUE_KEY = "job_queue"
SHUTDOWN = False


def _handle_signal(signum: int, frame: object) -> None:
    global SHUTDOWN
    logger.info(
        "Worker received shutdown signal", extra={"context": {"signal": signum}}
    )
    SHUTDOWN = True


async def process_job(job: dict[str, object]) -> None:
    """Dispatch a job to the appropriate handler. Idempotent."""
    import uuid as _uuid

    job_id = job.get("job_id", "unknown")
    job_type = job.get("job_type", "unknown")
    logger.info(
        "Processing job", extra={"context": {"job_id": job_id, "job_type": job_type}}
    )

    if job_type == "avatar_generation":
        from app.avatars.generation_service import run_generation_job

        await run_generation_job(_uuid.UUID(str(job_id)))
        return

    logger.warning(
        "No handler registered for job type",
        extra={"context": {"job_id": job_id, "job_type": job_type}},
    )


def _make_redis_client(redis_url: str) -> "Any":
    import redis.asyncio as aioredis

    # socket_timeout must exceed the blpop timeout so the client doesn't
    # raise before blpop's own timeout returns None on an empty queue.
    return aioredis.from_url(redis_url, socket_timeout=BLPOP_TIMEOUT + 2)  # type: ignore[no-untyped-call]


BLPOP_TIMEOUT = 5


async def run_worker() -> None:
    cfg = get_config()
    setup_logging(service="worker", level=cfg.LOG_LEVEL)

    from redis.exceptions import TimeoutError as RedisTimeoutError

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    logger.info("Worker started", extra={"context": {"queue": QUEUE_KEY}})

    client = _make_redis_client(cfg.REDIS_URL)

    while not SHUTDOWN:
        try:
            item = await client.blpop(QUEUE_KEY, timeout=BLPOP_TIMEOUT)
            if item is None:
                continue
            _, raw = item
            job = json.loads(raw)
            await process_job(job)
        except RedisTimeoutError:
            # Empty queue — normal; loop back and wait again
            continue
        except Exception as exc:
            logger.error("Worker error", extra={"context": {"error": str(exc)}})
            # Recreate the client so a broken connection doesn't persist.
            try:
                await client.aclose()
            except Exception:
                pass
            client = _make_redis_client(cfg.REDIS_URL)
            await asyncio.sleep(1)

    await client.aclose()
    logger.info("Worker stopped")


if __name__ == "__main__":
    asyncio.run(run_worker())
