from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Meridian"
    environment: str = "dev"
    api_key: str | None = None
    database_url: str = "sqlite+aiosqlite:///./meridian.db"
    redis_url: str = "redis://localhost:6379/0"
    redis_channel: str = "meridian.positions"
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    model_config = SettingsConfigDict(
        env_prefix="MERIDIAN_",
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
