from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Max Agent Backend"
    app_env: str = "development"
    api_prefix: str = "/api"
    debug: bool = True
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/max_agent"
    redis_url: str = "redis://localhost:6379/0"

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "max-agent"
    minio_secure: bool = False

    auth_secret: str = "max-agent-dev-secret"
    access_token_ttl_minutes: int = 30

    @property
    def access_token_ttl_seconds(self) -> int:
        return self.access_token_ttl_minutes * 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
