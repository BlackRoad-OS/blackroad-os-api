"""Placeholder Pydantic models for API requests and responses."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str


class VersionResponse(BaseModel):
    """Version response model."""

    version: str
