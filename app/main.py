from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.errors import ErrorHandlerMiddleware
from app.middleware.request_id import RequestIdMiddleware
from app.routes import root
from app.routes.v1.router import router as v1_router

app = FastAPI(title="BlackRoad Public API Gateway", version="0.1.0")

app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(root.router)
app.include_router(v1_router)


@app.get("/", include_in_schema=False)
async def index():
    return {"message": "BlackRoad public API gateway", "docs": "/docs"}
