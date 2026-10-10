from __future__ import annotations

import asyncio
import io
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from infrastructure.config import get_config
from infrastructure.logging import get_logger

if TYPE_CHECKING:
    from infrastructure.ai.interfaces import AvatarGenerationProvider
    from infrastructure.storage.interfaces import ObjectStorage

logger = get_logger(__name__)

_MAX_ATTEMPTS = 3
_IMAGE_SIZE = 1024
_MAX_FILE_BYTES = 5 * 1024 * 1024
_THUMBNAIL_SIZES = [("medium", 512), ("small", 256), ("thumb", 128)]
_RETRY_BACKOFF_SECONDS = [30, 120, 480]


def _backoff_seconds(attempt_just_failed: int) -> int:
    """Return seconds to sleep before the next attempt. attempt_just_failed is 1-indexed."""
    idx = attempt_just_failed - 1
    return _RETRY_BACKOFF_SECONDS[min(idx, len(_RETRY_BACKOFF_SECONDS) - 1)]


def _validate_image(image_bytes: bytes) -> dict[str, bool]:
    from PIL import Image

    try:
        img = Image.open(io.BytesIO(image_bytes))
        return {
            "dimensions": img.size == (_IMAGE_SIZE, _IMAGE_SIZE),
            "has_alpha": img.mode == "RGBA",
            "file_size": len(image_bytes) < _MAX_FILE_BYTES,
            "not_empty": img.getbbox() is not None,
        }
    except Exception as exc:
        logger.warning("Image validation error", extra={"context": {"error": str(exc)}})
        return {
            "dimensions": False,
            "has_alpha": False,
            "file_size": False,
            "not_empty": False,
        }


def _generate_thumbnails(image_bytes: bytes) -> dict[str, bytes]:
    from PIL import Image

    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    result: dict[str, bytes] = {}
    for label, size in _THUMBNAIL_SIZES:
        thumb = img.resize((size, size), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        thumb.save(buf, format="PNG")
        result[label] = buf.getvalue()
    return result


def _llm_user_prompt(avatar: Any) -> str:
    accessories_str = ", ".join(avatar.accessories) if avatar.accessories else "none"
    return (
        f"Create a character profile for a {avatar.species} with "
        f"{avatar.fur_color} fur, {avatar.eye_color} eyes, {avatar.hairstyle} hairstyle, "
        f"accessories: {accessories_str}, "
        f"wearing {avatar.clothes_top_color} top and {avatar.clothes_bottom_color} shorts."
    )


async def run_generation_job(job_id: uuid.UUID) -> None:
    """Execute the full avatar generation pipeline for a queued job."""
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    import infrastructure.database.models  # noqa: F401
    from app.avatars.repository import SQLAlchemyAvatarRepository
    from infrastructure.ai.openai_provider import OpenAIAvatarGenerationProvider
    from infrastructure.storage.s3_storage import S3ObjectStorage

    cfg = get_config()
    engine = create_async_engine(cfg.DATABASE_URL.get_secret_value())

    async with AsyncSession(engine, expire_on_commit=False) as session:
        async with session.begin():
            repo = SQLAlchemyAvatarRepository(session)
            job = await repo.get_job(job_id)
            if job is None:
                logger.warning("Job not found", extra={"context": {"job_id": str(job_id)}})
                return
            if job.status not in ("queued", "generating", "retrying"):
                logger.info(
                    "Job already processed",
                    extra={"context": {"job_id": str(job_id), "status": job.status}},
                )
                return

            avatar = await repo.get(job.avatar_id)

        await _run_pipeline(
            job_id=job_id,
            avatar=avatar,
            repo_factory=lambda s: SQLAlchemyAvatarRepository(s),
            engine=engine,
            ai_provider=OpenAIAvatarGenerationProvider(),
            object_storage=S3ObjectStorage(),
        )

    await engine.dispose()


async def _run_pipeline(
    job_id: uuid.UUID,
    avatar: Any,
    repo_factory: Any,
    engine: Any,
    ai_provider: AvatarGenerationProvider,
    object_storage: ObjectStorage,
) -> None:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.avatars.prompt_builder import build_character_prompt

    start = datetime.now(UTC)
    error_msg: str | None = None

    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            async with AsyncSession(engine, expire_on_commit=False) as session:
                async with session.begin():
                    repo = repo_factory(session)
                    job = await repo.get_job(job_id)
                    if job is None:
                        return
                    job.status = "llm_running"
                    job.attempt = attempt
                    await repo.update_job(job)

            # LLM call for character metadata
            user_prompt = _llm_user_prompt(avatar)
            metadata = await ai_provider.generate_metadata(user_prompt)
            metadata["species"] = avatar.species
            metadata["fur_color"] = avatar.fur_color
            metadata["eye_color"] = avatar.eye_color
            metadata["hairstyle"] = avatar.hairstyle
            metadata["accessories"] = list(avatar.accessories or [])
            metadata["clothes_top_color"] = avatar.clothes_top_color
            metadata["clothes_bottom_color"] = avatar.clothes_bottom_color

            # Build image prompt
            async with AsyncSession(engine, expire_on_commit=False) as session:
                async with session.begin():
                    repo = repo_factory(session)
                    job = await repo.get_job(job_id)
                    if job is None:
                        return
                    job.status = "prompt_building"
                    await repo.update_job(job)

            versioned_prompt = build_character_prompt(metadata, attempt=attempt)

            async with AsyncSession(engine, expire_on_commit=False) as session:
                async with session.begin():
                    repo = repo_factory(session)
                    job = await repo.get_job(job_id)
                    if job is None:
                        return
                    job.status = "generating"
                    job.prompt_version = versioned_prompt.prompt_version
                    await repo.update_job(job)

            # Generate image
            image_bytes = await ai_provider.generate_image(versioned_prompt.text)

            async with AsyncSession(engine, expire_on_commit=False) as session:
                async with session.begin():
                    repo = repo_factory(session)
                    job = await repo.get_job(job_id)
                    if job is None:
                        return
                    job.status = "validating"
                    await repo.update_job(job)

            # Validate
            checks = _validate_image(image_bytes)
            if not all(checks.values()):
                failed = [k for k, v in checks.items() if not v]
                logger.warning(
                    "Image validation failed",
                    extra={
                        "context": {
                            "job_id": str(job_id),
                            "attempt": attempt,
                            "failed_checks": failed,
                        }
                    },
                )
                error_msg = f"Validation failed: {failed}"
                continue
            safety_checks = await ai_provider.validate_child_safety(image_bytes)
            if not all(safety_checks.values()):
                failed = [key for key, value in safety_checks.items() if not value]
                logger.warning(
                    "Image safety validation failed",
                    extra={
                        "context": {
                            "job_id": str(job_id),
                            "attempt": attempt,
                            "failed_checks": failed,
                        }
                    },
                )
                error_msg = "Image did not pass the required child-safety checks."
                continue

            # Store PNG + thumbnails
            async with AsyncSession(engine, expire_on_commit=False) as session:
                async with session.begin():
                    repo = repo_factory(session)
                    job = await repo.get_job(job_id)
                    if job is None:
                        return
                    job.status = "storing"
                    await repo.update_job(job)

            thumbnails = _generate_thumbnails(image_bytes)
            base_key = f"characters/{avatar.account_id}/{avatar.id}/v{attempt}"
            full_url = object_storage.upload_png(f"{base_key}/portrait.png", image_bytes)
            medium_url = object_storage.upload_png(
                f"{base_key}/portrait_512.png", thumbnails["medium"]
            )
            small_url = object_storage.upload_png(
                f"{base_key}/portrait_256.png", thumbnails["small"]
            )
            thumb_url = object_storage.upload_png(
                f"{base_key}/portrait_128.png", thumbnails["thumb"]
            )

            model_version = ai_provider.image_model_version

            # Save portrait and update avatar/job
            async with AsyncSession(engine, expire_on_commit=False) as session:
                async with session.begin():
                    repo = repo_factory(session)
                    next_version = await repo.next_portrait_version(avatar.id)
                    portrait = await repo.create_portrait(
                        {
                            "avatar_id": avatar.id,
                            "version": next_version,
                            "prompt_version": versioned_prompt.prompt_version,
                            "model_version": model_version,
                            "full_url": full_url,
                            "medium_url": medium_url,
                            "small_url": small_url,
                            "thumb_url": thumb_url,
                        }
                    )

                    from sqlalchemy import select

                    result = await session.execute(
                        select(type(avatar)).where(type(avatar).id == avatar.id)
                    )
                    db_avatar: Any = result.scalar_one()
                    db_avatar.name = metadata.get("name")
                    db_avatar.personality = metadata.get("personality")
                    db_avatar.biography = metadata.get("biography")
                    db_avatar.appearance_summary = metadata.get("appearance_summary")
                    db_avatar.favorite_subject = metadata.get("favorite_subject")
                    db_avatar.running_style = metadata.get("running_style")
                    db_avatar.status = "published"
                    db_avatar.active_portrait_id = portrait.id

                    job = await repo.get_job(job_id)
                    if job is None:
                        return
                    job.status = "complete"
                    job.portrait_id = portrait.id
                    job.model_version = model_version
                    job.completed_at = datetime.now(UTC)
                    await repo.update_job(job)

            logger.info(
                "Generation complete",
                extra={
                    "context": {
                        "job_id": str(job_id),
                        "avatar_id": str(avatar.id),
                        "attempt": attempt,
                        "duration_ms": int((datetime.now(UTC) - start).total_seconds() * 1000),
                    }
                },
            )
            return

        except Exception as exc:
            error_msg = str(exc)
            logger.warning(
                "Generation attempt failed",
                extra={
                    "context": {
                        "job_id": str(job_id),
                        "attempt": attempt,
                        "error": error_msg,
                    }
                },
            )
            if attempt < _MAX_ATTEMPTS:
                backoff = _backoff_seconds(attempt)
                async with AsyncSession(engine, expire_on_commit=False) as session:
                    async with session.begin():
                        repo = repo_factory(session)
                        job = await repo.get_job(job_id)
                        if job is None:
                            return
                        job.status = "retrying"
                        await repo.update_job(job)
                await asyncio.sleep(backoff)

    # All attempts exhausted
    async with AsyncSession(engine, expire_on_commit=False) as session:
        async with session.begin():
            from sqlalchemy import select as _select

            from app.avatars.models import Avatar as _Avatar

            repo = repo_factory(session)
            job = await repo.get_job(job_id)
            if job:
                job.status = "permanent_failure"
                job.error = "Avatar could not be created. Please try again later."
                job.completed_at = datetime.now(UTC)
                await repo.update_job(job)

            result = await session.execute(_select(_Avatar).where(_Avatar.id == avatar.id))
            db_avatar = result.scalar_one_or_none()
            if db_avatar and db_avatar.status == "pending":
                db_avatar.status = "failed"

    logger.error(
        "Generation failed after all attempts",
        extra={
            "context": {
                "job_id": str(job_id),
                "avatar_id": str(avatar.id),
                "error": error_msg,
            }
        },
    )
