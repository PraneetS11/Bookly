from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: Literal["development", "test", "production"] = "development"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]
    DATABASE_URL: str
    JWT_SECRET_KEY: SecretStr = Field(min_length=32)
    JWT_ALGORITHM: Literal["HS256"] = "HS256"
    REDIS_URL: str = "redis://127.0.0.1:6381/0"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


Config = Settings()
