from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: Literal["development", "test", "production"] = "development"
    database_url: str = "sqlite:///./blog.db"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    seed_admin_enabled: bool = True
    seed_admin_username: str = "admin"
    seed_admin_password: str = "admin"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if (
        settings.app_env == "production"
        and settings.jwt_secret_key == "change-me-in-production"
    ):
        raise RuntimeError("JWT_SECRET_KEY must be set in production")
    return settings


settings = get_settings()
