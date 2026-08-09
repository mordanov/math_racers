"""Unit tests for AccountDomainService (T019)."""

from __future__ import annotations

import time
import uuid

import pytest

from app.accounts.domain_service import AccountDomainService
from app.shared.exceptions import PermissionError
from infrastructure.config import Config


def _make_config(**overrides: object) -> Config:
    defaults: dict[str, object] = {
        "DATABASE_URL": "postgresql+asyncpg://u:p@localhost/db",
        "REDIS_URL": "redis://localhost:6379/0",
        "JWT_SECRET": "test-secret-that-is-long-enough-32chars",
        "OPENAI_API_KEY": "sk-test",
        "STORAGE_ENDPOINT": "http://localhost:9000",
        "STORAGE_ACCESS_KEY": "minio",
        "STORAGE_SECRET_KEY": "minio123",
        "STORAGE_BUCKET": "test",
        "ADMIN_EMAIL": "admin@example.com",
        "ADMIN_PASSWORD": "adminpass123",
    }
    defaults.update(overrides)
    return Config.model_validate(defaults)


@pytest.fixture
def svc() -> AccountDomainService:
    return AccountDomainService()


@pytest.fixture
def cfg() -> Config:
    return _make_config()


@pytest.mark.unit
class TestPasswordHashing:
    def test_hash_and_verify_roundtrip(self, svc: AccountDomainService) -> None:
        plain = "s3cr3tP@ssword"
        hashed = svc.hash_password(plain)
        assert svc.verify_password(plain, hashed) is True

    def test_wrong_password_returns_false(self, svc: AccountDomainService) -> None:
        hashed = svc.hash_password("correct")
        assert svc.verify_password("wrong", hashed) is False

    def test_hash_is_different_each_time(self, svc: AccountDomainService) -> None:
        h1 = svc.hash_password("same")
        h2 = svc.hash_password("same")
        assert h1 != h2


@pytest.mark.unit
class TestJwtTokens:
    def test_encode_decode_roundtrip(self, svc: AccountDomainService, cfg: Config) -> None:
        account_id = uuid.uuid4()
        token = svc.create_access_token(account_id, "parent", cfg)
        payload = svc.decode_access_token(token, cfg)
        assert payload["sub"] == str(account_id)
        assert payload["role"] == "parent"

    def test_expired_token_raises_permission_error(self, svc: AccountDomainService) -> None:
        cfg = _make_config(JWT_ACCESS_TTL_MINUTES=0)
        account_id = uuid.uuid4()
        token = svc.create_access_token(account_id, "parent", cfg)
        # Sleep briefly to ensure expiry (TTL=0 means exp == iat)
        time.sleep(0.1)
        with pytest.raises(PermissionError) as exc_info:
            svc.decode_access_token(token, cfg)
        assert exc_info.value.error_code == "TOKEN_EXPIRED"

    def test_invalid_signature_raises_permission_error(
        self, svc: AccountDomainService, cfg: Config
    ) -> None:
        account_id = uuid.uuid4()
        token = svc.create_access_token(account_id, "parent", cfg)
        # Tamper with the token payload
        parts = token.split(".")
        tampered = parts[0] + "." + parts[1] + "x" + "." + parts[2]
        with pytest.raises(PermissionError) as exc_info:
            svc.decode_access_token(tampered, cfg)
        assert exc_info.value.error_code == "INVALID_TOKEN"

    def test_wrong_secret_raises_permission_error(
        self, svc: AccountDomainService, cfg: Config
    ) -> None:
        account_id = uuid.uuid4()
        token = svc.create_access_token(account_id, "parent", cfg)
        wrong_cfg = _make_config(**{"JWT_SECRET": "completely-different-secret-value!!"})
        with pytest.raises(PermissionError) as exc_info:
            svc.decode_access_token(token, wrong_cfg)
        assert exc_info.value.error_code == "INVALID_TOKEN"


@pytest.mark.unit
class TestRefreshTokenGeneration:
    def test_returns_tuple_of_raw_and_hash(self, svc: AccountDomainService) -> None:
        raw, token_hash = svc.generate_refresh_token()
        assert len(raw) > 0
        assert len(token_hash) == 64  # SHA-256 hex digest

    def test_unique_on_each_call(self, svc: AccountDomainService) -> None:
        raw1, _ = svc.generate_refresh_token()
        raw2, _ = svc.generate_refresh_token()
        assert raw1 != raw2

    def test_hash_is_sha256_of_raw(self, svc: AccountDomainService) -> None:
        import hashlib

        raw, token_hash = svc.generate_refresh_token()
        expected = hashlib.sha256(raw.encode()).hexdigest()
        assert token_hash == expected
