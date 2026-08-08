"""Background worker — processes jobs from the Redis queue."""

import asyncio
import json
import logging
import signal

from infrastructure.config import get_config
from infrastructure.logging import setup_logging, get_logger

logger = get_logger(__name__)

QUEUE_KEY = "job_queue"
SHUTDOWN = False


def _handle_signal(signum: int, frame: object) -> None:
    global SHUTDOWN
    logger.info("Worker received shutdown signal", extra={"context": {"signal": signum}})
    SHUTDOWN = True


async def process_job(job: dict) -> None:
    """Dispatch a job to the appropriate handler. Idempotent."""
    job_id = job.get("job_id", "unknown")
    job_type = job.get("job_type", "unknown")
    logger.info("Processing job", extra={"context": {"job_id": job_id, "job_type": job_type}})
    # Handlers for each job_type will be registered here as domain modules are built.
    # For now, log unknown job types without failing.
    logger.warning(
        "No handler registered for job type",
        extra={"context": {"job_id": job_id, "job_type": job_type}},
    )


async def run_worker() -> None:
    cfg = get_config()
    setup_logging(service="worker", level=cfg.LOG_LEVEL)

    import redis.asyncio as aioredis
    from redis.exceptions import TimeoutError as RedisTimeoutError

    # socket_timeout must exceed the blpop timeout so the client doesn't
    # raise before blpop's own timeout returns None on an empty queue.
    BLPOP_TIMEOUT = 5
    client = aioredis.from_url(cfg.REDIS_URL, socket_timeout=BLPOP_TIMEOUT + 2)

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    logger.info("Worker started", extra={"context": {"queue": QUEUE_KEY}})

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
            await asyncio.sleep(1)

    await client.aclose()
    logger.info("Worker stopped")


if __name__ == "__main__":
    asyncio.run(run_worker())
