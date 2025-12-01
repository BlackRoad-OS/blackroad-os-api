"""Application entrypoint for blackroad-os-api."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

from app import __version__
from app.generated.router import router as generated_router
from app.middleware.response_headers import ResponseHeaderMiddleware
from app.rate_limiting import limiter


app = FastAPI(
    title="BlackRoad OS Public API",
    description="Public-facing gateway for BlackRoad services",
    version=__version__,
)

app.state.limiter = limiter

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ResponseHeaderMiddleware)

app.include_router(generated_router)


@app.get("/", include_in_schema=False)
async def index():
    return {"message": "BlackRoad public API gateway", "docs": "/docs"}


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}
