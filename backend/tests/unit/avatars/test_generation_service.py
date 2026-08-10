"""Unit tests for GenerationService pipeline internals with mocked providers."""

from __future__ import annotations

import io

from PIL import Image

from app.avatars.generation_service import (
    _generate_thumbnails,
    _validate_image,
)


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
