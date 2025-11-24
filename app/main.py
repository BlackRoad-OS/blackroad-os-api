"""Application entrypoint for blackroad-os-api."""

from time import perf_counter

from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.core.logging import configure_logging
from app.core.settings import settings
from app.workers.sample_task import celery_app


def create_app() -> FastAPI:
    """Instantiate the FastAPI application."""

    configure_logging()
    application = FastAPI(title=settings.app_name, version=settings.version)
    application.state.settings = settings
    # TODO(celery-integration): Celery app is stored for future use. Integrate Celery tasks with FastAPI endpoints in upcoming releases.
    application.state.celery_app = celery_app
    application.state.start_time = perf_counter()

    # TODO(api-next): add authentication, rate limiting, and tracing middleware.
    application.include_router(v1_router)
    return application


app = create_app()
__all__ = ["app"]
