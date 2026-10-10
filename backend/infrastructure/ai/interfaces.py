from __future__ import annotations

from typing import Any, Protocol


class AvatarGenerationProvider(Protocol):
    image_model_version: str

    async def generate_metadata(self, prompt: str) -> dict[str, Any]: ...
    async def generate_image(self, prompt: str) -> bytes: ...
    async def validate_child_safety(self, image_bytes: bytes) -> dict[str, bool]: ...
