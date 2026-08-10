from __future__ import annotations

import io
import uuid
from datetime import UTC, datetime
from typing import Any

from infrastructure.config import get_config
from infrastructure.logging import get_logger

logger = get_logger(__name__)

_LLM_SYSTEM_PROMPT = (
    "You are a creative writer for a children's educational game. "
    "Generate a fun, positive, age-appropriate character profile for a racing character. "
    "Respond with valid JSON matching the provided schema exactly."
)

_LLM_METADATA_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "personality": {"type": "string"},
        "biography": {"type": "string"},
        "appearance_summary": {"type": "string"},
        "species": {"type": "string"},
        "favorite_color": {"type": "string"},
        "favorite_subject": {"type": "string"},
        "running_style": {"type": "string"},
    },
    "required": [
        "name",
        "personality",
        "biography",
        "appearance_summary",
        "species",
        "favorite_color",
        "favorite_subject",
        "running_style",
    ],
    "additionalProperties": False,
}

_MAX_ATTEMPTS = 3
_IMAGE_SIZE = 1024
_MAX_FILE_BYTES = 5 * 1024 * 1024
_THUMBNAIL_SIZES = [("medium", 512), ("small", 256), ("thumb", 128)]


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
        return {"dimensions": False, "has_alpha": False, "file_size": False, "not_empty": False}


def _generate_thumbnails(image_bytes: bytes) -> dict[str, bytes]:
    from PIL import Image

    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    result: dict[str, bytes] = {}
    for label, size in _THUMBNAIL_SIZES:
        thumb = img.resize((size, size), Image.LANCZOS)
        buf = io.BytesIO()
        thumb.save(buf, format="PNG")
        result[label] = buf.getvalue()
    return result


def _s3_client() -> Any:
    import boto3

    cfg = get_config()
    return boto3.client(
        "s3",
        endpoint_url=cfg.STORAGE_ENDPOINT,
        aws_access_key_id=cfg.STORAGE_ACCESS_KEY.get_secret_value(),
        aws_secret_access_key=cfg.STORAGE_SECRET_KEY.get_secret_value(),
    )


def _upload_png(s3: Any, key: str, data: bytes) -> str:
    cfg = get_config()
    s3.put_object(
        Bucket=cfg.STORAGE_BUCKET,
        Key=key,
        Body=data,
        ContentType="image/png",
    )
    return f"{cfg.STORAGE_ENDPOINT}/{cfg.STORAGE_BUCKET}/{key}"


def _llm_user_prompt(avatar: Any) -> str:
    accessories_str = ", ".join(avatar.accessories) if avatar.accessories else "none"
    return (
        f"Create a character profile for a {avatar.species} with "
        f"{avatar.fur_color} fur, {avatar.eye_color} eyes, {avatar.hairstyle} hairstyle, "
        f"accessories: {accessories_str}, "
        f"wearing {avatar.clothes_top_color} top and {avatar.clothes_bottom_color} shorts."
    )


async def _call_llm(user_prompt: str) -> dict[str, Any]:
    import json

    from openai import AsyncOpenAI

    cfg = get_config()
    client = AsyncOpenAI(api_key=cfg.OPENAI_API_KEY.get_secret_value())
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _LLM_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.8,
    )
    raw = response.choices[0].message.content or "{}"
    return dict(json.loads(raw))


async def _call_image_api(prompt: str) -> bytes:
    import base64

    from openai import AsyncOpenAI

    cfg = get_config()
    client = AsyncOpenAI(api_key=cfg.OPENAI_API_KEY.get_secret_value())
    response = await client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024",
        quality="hd",
        response_format="b64_json",
    )
    b64 = response.data[0].b64_json or ""
    return base64.b64decode(b64)


async def run_generation_job(job_id: uuid.UUID) -> None:
    """Execute the full avatar generation pipeline for a queued job."""
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    from app.avatars.models import Avatar, AvatarPortrait, GenerationJob
    from app.avatars.prompt_builder import build_character_prompt
    from app.avatars.repository import SQLAlchemyAvatarRepository

    cfg = get_config()
    engine = create_async_engine(cfg.DATABASE_URL.get_secret_value())

    async with AsyncSession(engine, expire_on_commit=False) as session:
        async with session.begin():
            repo = SQLAlchemyAvatarRepository(session)
            job = await repo.get_job(job_id)
            if job is None:
                logger.warning("Job not found", extra={"context": {"job_id": str(job_id)}})
                return
            if job.status not in ("queued", "generating"):
                logger.info(
                    "Job already processed",
                    extra={"context": {"job_id": str(job_id), "status": job.status}},
                )
                return

            avatar = await repo.get(job.avatar_id)

        await _run_pipeline(job_id=job_id, avatar=avatar, repo_factory=lambda s: SQLAlchemyAvatarRepository(s), engine=engine)

    await engine.dispose()


async def _run_pipeline(
    job_id: uuid.UUID,
    avatar: Any,
    repo_factory: Any,
    engine: Any,
) -> None:
    from app.avatars.prompt_builder import build_character_prompt
    from sqlalchemy.ext.asyncio import AsyncSession

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
            metadata = await _call_llm(user_prompt)
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
            image_bytes = await _call_image_api(versioned_prompt.text)

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
            s3 = _s3_client()
            base_key = f"characters/{avatar.account_id}/{avatar.id}/v{attempt}"
            full_url = _upload_png(s3, f"{base_key}/portrait.png", image_bytes)
            medium_url = _upload_png(s3, f"{base_key}/portrait_512.png", thumbnails["medium"])
            small_url = _upload_png(s3, f"{base_key}/portrait_256.png", thumbnails["small"])
            thumb_url = _upload_png(s3, f"{base_key}/portrait_128.png", thumbnails["thumb"])

            # Determine OpenAI model version from API response (use constant for now)
            model_version = "dall-e-3"

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
                    db_avatar = result.scalar_one()
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

    # All attempts exhausted
    async with AsyncSession(engine, expire_on_commit=False) as session:
        async with session.begin():
            from sqlalchemy import select as _select
            from app.avatars.models import Avatar as _Avatar

            repo = repo_factory(session)
            job = await repo.get_job(job_id)
            if job:
                job.status = "failed"
                job.error = error_msg
                job.completed_at = datetime.now(UTC)
                await repo.update_job(job)

            result = await session.execute(
                _select(_Avatar).where(_Avatar.id == avatar.id)
            )
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
