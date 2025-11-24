"""Shared Pydantic schemas for the API."""

from pydantic import BaseModel, Field


class ExampleSchema(BaseModel):
    """Example payload schema for future endpoints."""

    message: str = Field(description="Sample message payload")
    count: int = Field(default=1, ge=0, description="Example counter")
