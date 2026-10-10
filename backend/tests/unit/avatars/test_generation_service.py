"""Unit tests for GenerationService pipeline internals with mocked providers."""

from __future__ import annotations

import io
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from PIL import Image

from app.avatars.generation_service import (
    _generate_thumbnails,
    _validate_image,
)
from infrastructure.ai.openai_provider import OpenAIAvatarGenerationProvider


def _make_png_bytes(size: int = 1024, mode: str = "RGBA") -> bytes:
    img = Image.new(mode, (size, size), color=(100, 150, 200, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ── _validate_image ───────────────────────────────────────────────────────────


def test_validate_valid_image() -> None:
    img_bytes = _make_png_bytes(1024, "RGBA")
    result = _validate_image(img_bytes)
    assert result["dimensions"] is True
    assert result["has_alpha"] is True
    assert result["file_size"] is True
    assert result["not_empty"] is True


def test_validate_wrong_dimensions() -> None:
    img_bytes = _make_png_bytes(512, "RGBA")
    result = _validate_image(img_bytes)
    assert result["dimensions"] is False


def test_validate_no_alpha() -> None:
    img_bytes = _make_png_bytes(1024, "RGB")
    result = _validate_image(img_bytes)
    assert result["has_alpha"] is False


def test_validate_corrupt_bytes() -> None:
    result = _validate_image(b"not-an-image")
    assert all(v is False for v in result.values())


def test_validate_all_pass_returns_dict() -> None:
    img_bytes = _make_png_bytes(1024, "RGBA")
    result = _validate_image(img_bytes)
    assert set(result.keys()) == {"dimensions", "has_alpha", "file_size", "not_empty"}


# ── _generate_thumbnails ──────────────────────────────────────────────────────


def test_generate_thumbnails_returns_three_sizes() -> None:
    img_bytes = _make_png_bytes(1024, "RGBA")
    result = _generate_thumbnails(img_bytes)
    assert set(result.keys()) == {"medium", "small", "thumb"}


def test_thumbnail_sizes() -> None:
    img_bytes = _make_png_bytes(1024, "RGBA")
    result = _generate_thumbnails(img_bytes)
    for label, expected_size in [("medium", 512), ("small", 256), ("thumb", 128)]:
        img = Image.open(io.BytesIO(result[label]))
        assert img.size == (expected_size, expected_size), f"{label} wrong size"


def test_thumbnails_are_png() -> None:
    img_bytes = _make_png_bytes(1024, "RGBA")
    result = _generate_thumbnails(img_bytes)
    for label, data in result.items():
        img = Image.open(io.BytesIO(data))
        assert img.format == "PNG", f"{label} not PNG"


@pytest.mark.asyncio
async def test_metadata_generation_uses_configured_model() -> None:
    completion = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content='{"name":"Racer"}'))]
    )
    client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=AsyncMock(return_value=completion)))
    )
    config = SimpleNamespace(
        OPENAI_API_KEY=SimpleNamespace(get_secret_value=lambda: "key"),
        OPENAI_AVATAR_METADATA_MODEL="custom-metadata-model",
    )

    with (
        patch("openai.AsyncOpenAI", return_value=client),
        patch("infrastructure.ai.openai_provider.get_config", return_value=config),
    ):
        result = await OpenAIAvatarGenerationProvider().generate_metadata("prompt")

    assert result == {"name": "Racer"}
    assert client.chat.completions.create.await_args.kwargs["model"] == "custom-metadata-model"


@pytest.mark.asyncio
async def test_image_generation_uses_configured_model() -> None:
    generated_image = SimpleNamespace(data=[SimpleNamespace(b64_json="aW1hZ2U=")])
    client = SimpleNamespace(
        images=SimpleNamespace(generate=AsyncMock(return_value=generated_image))
    )
    config = SimpleNamespace(
        OPENAI_API_KEY=SimpleNamespace(get_secret_value=lambda: "key"),
        OPENAI_AVATAR_IMAGE_MODEL="custom-image-model",
    )
    provider = OpenAIAvatarGenerationProvider()

    with (
        patch("openai.AsyncOpenAI", return_value=client),
        patch("infrastructure.ai.openai_provider.get_config", return_value=config),
    ):
        image = await provider.generate_image("prompt")
        image_model_version = provider.image_model_version

    assert image == b"image"
    assert image_model_version == "custom-image-model"
    assert client.images.generate.await_args.kwargs["model"] == "custom-image-model"


@pytest.mark.asyncio
async def test_child_safety_requires_every_approved_check() -> None:
    checks = {
        "safe": True,
        "single_character": True,
        "full_body": True,
        "no_text": True,
        "no_watermark": True,
    }
    completion = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(checks)))]
    )
    client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=AsyncMock(return_value=completion)))
    )
    config = SimpleNamespace(
        OPENAI_API_KEY=SimpleNamespace(get_secret_value=lambda: "key"),
        OPENAI_AVATAR_SAFETY_MODEL="custom-safety-model",
    )

    with (
        patch("openai.AsyncOpenAI", return_value=client),
        patch("infrastructure.ai.openai_provider.get_config", return_value=config),
    ):
        result = await OpenAIAvatarGenerationProvider().validate_child_safety(b"image")

    assert result == checks
    assert client.chat.completions.create.await_args.kwargs["model"] == "custom-safety-model"


@pytest.mark.asyncio
async def test_child_safety_rejects_incomplete_provider_result() -> None:
    completion = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content='{"safe": true}'))]
    )
    client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=AsyncMock(return_value=completion)))
    )
    config = SimpleNamespace(
        OPENAI_API_KEY=SimpleNamespace(get_secret_value=lambda: "key"),
        OPENAI_AVATAR_SAFETY_MODEL="custom-safety-model",
    )

    with (
        patch("openai.AsyncOpenAI", return_value=client),
        patch("infrastructure.ai.openai_provider.get_config", return_value=config),
        pytest.raises(ValueError, match="invalid result"),
    ):
        await OpenAIAvatarGenerationProvider().validate_child_safety(b"image")
