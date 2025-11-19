from __future__ import annotations

from app.clients.upstream import UpstreamClient
from app.config import Settings


def build_core_client(settings: Settings) -> UpstreamClient:
    return UpstreamClient(
        "core",
        str(settings.core_api_url) if settings.core_api_url else None,
        default_timeout=settings.request_timeout_seconds,
    )
