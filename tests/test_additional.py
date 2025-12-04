"""Additional coverage tests for auxiliary modules."""

import logging
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.router import router as legacy_router
from app.core.logging import configure_logging, logger
from app.core.settings import settings
from app.main import app
from app.models.common import BaseModel as CommonBaseModel
from app.workers.sample_task import celery_app, log_payload
from pydantic import BaseModel as PydanticBaseModel


def test_index_route_includes_docs_link():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"


def test_legacy_router_health_and_version():
    legacy_app = FastAPI()
    legacy_app.state.start_time = 0.0
    legacy_app.state.settings = settings
    legacy_app.include_router(legacy_router)
    client = TestClient(legacy_app)

    health = client.get("/health").json()
    assert health["status"] == "ok"
    assert health["uptime"] >= 0

    version = client.get("/version").json()
    assert version == {"version": settings.version, "commit": settings.git_sha}


def test_logging_configuration_sets_level():
    configure_logging(level=logging.DEBUG)
    assert logger.level == logging.DEBUG


def test_common_model_alias():
    assert CommonBaseModel is PydanticBaseModel


def test_sample_task_echoes_payload():
    payload = {"foo": "bar"}
    result = log_payload(payload)
    assert result == payload
    assert celery_app.main == settings.app_name
