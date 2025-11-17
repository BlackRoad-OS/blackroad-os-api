"""FastAPI main application with health and version endpoints."""

from fastapi import FastAPI

from app import __version__

app = FastAPI(
    title="BlackRoad OS API",
    description="Minimal API service for BlackRoad OS",
    version=__version__,
)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/version")
async def version():
    """Version endpoint."""
    return {"version": __version__}
