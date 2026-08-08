from enum import Enum
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    development = "development"
    staging = "staging"
    production = "production"


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        # SecretStr fields are masked in model repr — never expose raw values
    )

    # Database
    DATABASE_URL: SecretStr

    # Cache / Queue
    REDIS_URL: str

    # Authentication
    JWT_SECRET: SecretStr

    # AI Provider
    OPENAI_API_KEY: SecretStr

    # Object Storage
    STORAGE_ENDPOINT: str
    STORAGE_ACCESS_KEY: SecretStr
    STORAGE_SECRET_KEY: SecretStr
    STORAGE_BUCKET: str

    # Application
    ENVIRONMENT: Environment = Environment.development
    VERSION: str = "dev"
    LOG_LEVEL: str = "INFO"

    # Alert thresholds (US5)
    ALERT_ERROR_RATE_THRESHOLD: float = 0.01
    ALERT_AI_FAILURE_RATE_THRESHOLD: float = 0.10
    ALERT_QUEUE_DEPTH_THRESHOLD: int = 500
    ALERT_DB_P95_MS_THRESHOLD: int = 500

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: object) -> object:
        url = str(v) if not isinstance(v, SecretStr) else v.get_secret_value()
        if not url.startswith(("postgresql", "postgres")):
            raise ValueError("DATABASE_URL must be a PostgreSQL DSN")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid:
            raise ValueError(f"LOG_LEVEL must be one of {valid}")
        return v.upper()


_config: Config | None = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config()  # type: ignore[call-arg]
    return _config
