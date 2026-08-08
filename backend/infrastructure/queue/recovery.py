import logging
from datetime import datetime, timedelta, timezone

from infrastructure.logging import get_logger

logger = get_logger(__name__)

PENDING_JOB_AGE_MINUTES = 5


async def recover_pending_jobs() -> None:
    """Re-enqueue pending jobs from job_audit that are older than the threshold.

    Called on application startup after migrations are confirmed current.
    Jobs that were enqueued but never processed (e.g. due to a Redis restart)
    are re-submitted to the Redis queue.
    """
    try:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy import text

        from infrastructure.config import get_config
        import redis.asyncio as aioredis

        cfg = get_config()
        engine = create_async_engine(cfg.DATABASE_URL.get_secret_value())
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=PENDING_JOB_AGE_MINUTES)

        async with AsyncSession(engine) as session:
            result = await session.execute(
                text(
                    "SELECT job_id, job_type, payload FROM job_audit "
                    "WHERE status = 'pending' AND created_at < :cutoff"
                ),
                {"cutoff": cutoff},
            )
            rows = result.fetchall()

        if not rows:
            logger.info("Job recovery: no pending jobs to re-enqueue")
            await engine.dispose()
            return

        client = aioredis.from_url(cfg.REDIS_URL)
        import json as _json

        requeued = 0
        for row in rows:
            job = {
                "job_id": str(row.job_id),
                "job_type": row.job_type,
                "payload": row.payload,
            }
            await client.rpush("job_queue", _json.dumps(job))
            requeued += 1

        await client.aclose()
        await engine.dispose()

        logger.info(
            "Job recovery complete",
            extra={"context": {"requeued_count": requeued}},
        )
    except Exception as exc:
        logger.warning(
            "Job recovery failed — continuing startup",
            extra={"context": {"error": str(exc)}},
        )
