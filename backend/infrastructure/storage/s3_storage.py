from __future__ import annotations

from typing import Any

from infrastructure.config import get_config


class S3ObjectStorage:
    def __init__(self) -> None:
        import boto3

        cfg = get_config()
        self._client: Any = boto3.client(
            "s3",
            endpoint_url=cfg.STORAGE_ENDPOINT,
            aws_access_key_id=cfg.STORAGE_ACCESS_KEY.get_secret_value(),
            aws_secret_access_key=cfg.STORAGE_SECRET_KEY.get_secret_value(),
        )

    def upload_png(self, key: str, data: bytes) -> str:
        cfg = get_config()
        self._client.put_object(
            Bucket=cfg.STORAGE_BUCKET,
            Key=key,
            Body=data,
            ContentType="image/png",
        )
        return f"{cfg.STORAGE_ENDPOINT}/{cfg.STORAGE_BUCKET}/{key}"
