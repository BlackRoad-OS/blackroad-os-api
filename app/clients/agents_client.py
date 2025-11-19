from __future__ import annotations

from app.clients.upstream import UpstreamClient
from app.config import Settings


def build_agents_client(settings: Settings) -> UpstreamClient:
    return UpstreamClient(
        "agents",
        str(settings.agents_api_url) if settings.agents_api_url else None,
        default_timeout=settings.request_timeout_seconds,
    )
