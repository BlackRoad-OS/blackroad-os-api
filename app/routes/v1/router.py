from __future__ import annotations

from fastapi import APIRouter, Depends

from app.middleware.auth import api_key_auth
from app.routes.v1 import agents, core, health

router = APIRouter(prefix="/v1", dependencies=[Depends(api_key_auth)])
router.include_router(health.router)
router.include_router(core.router)
router.include_router(agents.router)
