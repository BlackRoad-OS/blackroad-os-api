from __future__ import annotations

import os
from datetime import datetime
from functools import lru_cache
from typing import List, Optional

from pydantic import AnyHttpUrl, Field, field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    env: str = Field("development", alias="NODE_ENV")
    public_api_url: Optional[AnyHttpUrl] = Field(None, alias="PUBLIC_API_URL")
    core_api_url: Optional[AnyHttpUrl] = Field(None, alias="CORE_API_URL")
    agents_api_url: Optional[AnyHttpUrl] = Field(None, alias="AGENTS_API_URL")

    api_keys: List[str] = Field(default_factory=list, alias="API_KEYS")
    public_api_key: Optional[str] = Field(None, alias="PUBLIC_API_KEY")
    app_version: str = Field("0.1.0", alias="APP_VERSION")
    build_time: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(), alias="BUILD_TIME"
    )
    commit: Optional[str] = Field(None, alias="GIT_COMMIT")

    log_level: str = Field("info", alias="LOG_LEVEL")
    port: int = Field(8000, alias="PORT")
    request_timeout_ms: int = Field(10000, alias="REQUEST_TIMEOUT_MS")

    model_config = {
        "case_sensitive": False,
        "populate_by_name": True,
    }

    @field_validator("commit", mode="before")
    @classmethod
    def prefer_railway_commit(cls, value: Optional[str]) -> Optional[str]:
        return value or os.getenv("RAILWAY_GIT_COMMIT_SHA")

    @field_validator("api_keys", mode="before")
    @classmethod
    def split_keys(cls, value: Optional[str]) -> List[str]:
        if value in (None, ""):
            return []
        if isinstance(value, str):
            return [key.strip() for key in value.split(",") if key.strip()]
        return value

    @model_validator(mode="after")
    @classmethod
    def validate_required(cls, values: "Settings") -> "Settings":
        if values.env.lower() != "development":
            missing = []
            if not values.public_api_url:
                missing.append("PUBLIC_API_URL")
            if not values.core_api_url:
                missing.append("CORE_API_URL")
            if not (values.api_keys or values.public_api_key):
                missing.append("API_KEYS or PUBLIC_API_KEY")
            if missing:
                raise ValueError(
                    f"Missing required environment variables: {', '.join(missing)}"
                )
        return values

    @property
    def core_configured(self) -> bool:
        return bool(self.core_api_url)

    @property
    def agents_configured(self) -> bool:
        return bool(self.agents_api_url)

    @property
    def request_timeout_seconds(self) -> float:
        return max(self.request_timeout_ms, 0) / 1000

    @property
    def allowed_api_keys(self) -> List[str]:
        keys: List[str] = []
        keys.extend(self.api_keys)
        if self.public_api_key:
            keys.append(self.public_api_key)
        # remove empties while preserving order
        return [key for key in keys if key]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
