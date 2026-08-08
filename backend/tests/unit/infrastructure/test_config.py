"""Unit tests: config validation and SecretStr serialisation safety."""

import pytest
from pydantic import SecretStr, ValidationError


@pytest.mark.unit
class TestConfigValidation:
    def _make_valid_env(self) -> dict:
        return {
            "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/db",
            "REDIS_URL": "redis://localhost:6379/0",
            "JWT_SECRET": "a" * 64,
            "OPENAI_API_KEY": "sk-" + "a" * 48,
            "STORAGE_ENDPOINT": "https://storage.example.com",
            "STORAGE_ACCESS_KEY": "access",
            "STORAGE_SECRET_KEY": "secret",
            "STORAGE_BUCKET": "bucket",
        }

    def test_valid_config_creates_successfully(self) -> None:
        from infrastructure.config import Config

        env = self._make_valid_env()
        cfg = Config(**env)  # type: ignore[call-arg]
        assert cfg.ENVIRONMENT.value == "development"

    def test_invalid_database_url_raises(self) -> None:
        from infrastructure.config import Config

        env = self._make_valid_env()
        env["DATABASE_URL"] = "mysql://user:pass@localhost/db"
        with pytest.raises(ValidationError, match="DATABASE_URL must be a PostgreSQL DSN"):
            Config(**env)  # type: ignore[call-arg]

    def test_invalid_environment_raises(self) -> None:
        from infrastructure.config import Config

        env = self._make_valid_env()
        env["ENVIRONMENT"] = "unknown"
        with pytest.raises(ValidationError):
            Config(**env)  # type: ignore[call-arg]

    def test_invalid_log_level_raises(self) -> None:
        from infrastructure.config import Config

        env = self._make_valid_env()
        env["LOG_LEVEL"] = "TRACE"
        with pytest.raises(ValidationError, match="LOG_LEVEL"):
            Config(**env)  # type: ignore[call-arg]

    def test_secret_str_fields_not_exposed_in_repr(self) -> None:
        from infrastructure.config import Config

        env = self._make_valid_env()
        cfg = Config(**env)  # type: ignore[call-arg]
        cfg_repr = repr(cfg)
        # SecretStr repr is "**********" — raw values must not appear
        assert "pass" not in cfg_repr
        assert env["JWT_SECRET"] not in cfg_repr
        assert env["OPENAI_API_KEY"] not in cfg_repr

    def test_secret_str_not_in_model_dump(self) -> None:
        from infrastructure.config import Config

        env = self._make_valid_env()
        cfg = Config(**env)  # type: ignore[call-arg]
        dumped = cfg.model_dump()
        # SecretStr appears as SecretStr object in dump, not raw string
        assert isinstance(dumped["JWT_SECRET"], SecretStr)
        assert isinstance(dumped["OPENAI_API_KEY"], SecretStr)
        # Access via .get_secret_value() — not leaking automatically
        assert dumped["JWT_SECRET"].get_secret_value() == env["JWT_SECRET"]
