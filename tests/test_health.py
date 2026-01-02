"""Smoke tests for health, ready, and version endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    """Test the /health endpoint returns proper liveness info."""
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "uptime" in payload
    assert payload["uptime"] >= 0


def test_ready_endpoint() -> None:
    """Test the /ready endpoint returns readiness info."""
    response = client.get("/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ready"] is True
    assert payload["service"] == "blackroad-os-api"


def test_version_endpoint() -> None:
    """Test the /version endpoint returns version metadata."""
    response = client.get("/version")
    assert response.status_code == 200
    payload = response.json()
    assert "service" in payload
    assert payload["service"] == "blackroad-os-api"
    assert "version" in payload
    assert "commit" in payload
    assert "env" in payload
