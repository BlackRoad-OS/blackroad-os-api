from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from typing import List, Optional

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    env: str = Field("development", alias="NODE_ENV")
    public_api_url: AnyHttpUrl = Field(..., alias="PUBLIC_API_URL")
    core_api_url: AnyHttpUrl = Field(..., alias="CORE_API_URL")
    agents_api_url: Optional[AnyHttpUrl] = Field(None, alias="AGENTS_API_URL")

    api_keys: List[str] = Field(default_factory=list, alias="API_KEYS")
    rate_limit_window: Optional[int] = Field(None, alias="RATE_LIMIT_WINDOW")
    rate_limit_max: Optional[int] = Field(None, alias="RATE_LIMIT_MAX")

    app_version: str = "0.1.0"
    build_time: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    commit: Optional[str] = Field(None, alias="GIT_COMMIT")

    model_config = {
        "case_sensitive": False,
        "populate_by_name": True,
    }

    @field_validator("api_keys", mode="before")
    @classmethod
    def split_keys(cls, value: Optional[str]) -> List[str]:
        if value in (None, ""):
            return []
        if isinstance(value, str):
            return [key.strip() for key in value.split(",") if key.strip()]
        return value

    @property
    def core_configured(self) -> bool:
        return bool(self.core_api_url)

    @property
    def agents_configured(self) -> bool:
        return bool(self.agents_api_url)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
