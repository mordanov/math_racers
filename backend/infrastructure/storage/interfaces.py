from __future__ import annotations

from typing import Protocol


class ObjectStorage(Protocol):
    def upload_png(self, key: str, data: bytes) -> str: ...
