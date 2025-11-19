from __future__ import annotations

from fastapi import APIRouter

from app.routes.v1 import agents, core, health

router = APIRouter(prefix="/v1")
router.include_router(health.router)
router.include_router(core.router)
router.include_router(agents.router)
