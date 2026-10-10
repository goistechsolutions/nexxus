from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="NEXXUS_", extra="ignore"
    )

    environment: Literal["dev", "hml", "prd"] = "dev"
    api_v1_prefix: str = "/v1"
    database_url: str = "postgresql+asyncpg://USER:PASSWORD@localhost:5432/nexxus"
    cors_origins: list[AnyHttpUrl] = Field(default_factory=list)
    oidc_issuer_url: str | None = None
    oidc_audience: str | None = None
    tenant_header: str = "X-Tenant-Id"


@lru_cache
def get_settings() -> Settings:
    return Settings()
