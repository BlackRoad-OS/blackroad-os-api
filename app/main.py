from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.errors import ErrorHandlerMiddleware
from app.middleware.request_id import RequestIdMiddleware
from app.routes import root
from app.routes.v1.router import router as v1_router

app = FastAPI(title="BlackRoad Public API Gateway", version="0.1.0")

# Middleware execution order: Last added = first executed (outermost layer)
# Request flow: ErrorHandler -> RequestId -> CORS -> App
# This ensures ErrorHandler can catch exceptions from all other middleware
app.add_middleware(
    CORSMiddleware,                          # First added = innermost
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.add_middleware(RequestIdMiddleware)      # Second added = middle layer
app.add_middleware(ErrorHandlerMiddleware)  # Last added = outermost, catches all errors

app.include_router(root.router)
app.include_router(v1_router)


@app.get("/", include_in_schema=False)
async def index():
    return {"message": "BlackRoad public API gateway", "docs": "/docs"}
