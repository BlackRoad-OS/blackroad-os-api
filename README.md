# Blackroad OS · API Service (Gen-0)

A minimal FastAPI 0.110 scaffold with Celery stubs for background work. Built to sit behind Operator & Prism layers.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# → http://127.0.0.1:8000/health
```

Docker:

```bash
docker build -t blackroad/api:0.0.1 . -f infra/Dockerfile
docker run -e PORT=8000 -p 8000:8000 blackroad/api:0.0.1
```

## Endpoints

- `GET /health` returns `{ "status": "ok", "uptime": seconds }`.
- `GET /version` returns `{ "version": "0.0.1", "commit": GIT_SHA }` sourced from environment.

## Tasks

Celery 5 is wired via `app/workers/sample_task.py`. Configure `CELERY_BROKER_URL` in the environment to dispatch jobs; the sample task logs and echoes incoming payloads.

## Configuration

Runtime settings live in `app/core/settings.py` using Pydantic v2 `BaseSettings`.
- `GIT_SHA` (default `unknown`) annotates the running commit.
- `CELERY_BROKER_URL` (default `memory://`) defines the Celery broker.
- `LOG_LEVEL` drives basic logging setup.

Copy `infra/api.env.example` to configure a local `.env`.

## Development

- Linting: `ruff check .`
- Formatting: `black .`
- Tests: `pytest`

# TODO(api-next): add authentication, rate limiting, and extended observability hooks.
# BlackRoad OS – Public API

`blackroad-os-api` is the FastAPI gateway that fronts every public BlackRoad surface (operator, core, packs, etc.). The API is driven by the contract in [`openapi.yaml`](./openapi.yaml) and generated with `fastapi-codegen`.

## Quick start

```bash
poetry install
make dev
```

The server listens on `http://localhost:${PORT:-8000}` and exposes docs at `/docs`.

### Environment variables

- `OPERATOR_URL` – Base URL for the operator service (required for agent proxy & installs)
- `PACK_INDEX_URL` – URL that returns a JSON list of `blackroad-os-pack-*` packages
- `API_KEYS` – Comma-separated API keys accepted in the `X-BR-KEY` header
- `PUBLIC_API_KEY` – Additional API key accepted in the `X-BR-KEY` header
- `GIT_COMMIT` – Git SHA used for the `X-API-Version` header
- `PORT` – HTTP port (default: `8000`)

### Example calls

```bash
curl -H "X-BR-KEY: your-api-key-here" http://localhost:8000/v1/agents
curl -H "X-BR-KEY: your-api-key-here" http://localhost:8000/v1/packs
curl -H "X-BR-KEY: your-api-key-here" -X POST http://localhost:8000/v1/packs/alpha/install
```

## Development

- Update the API surface by editing [`openapi.yaml`](./openapi.yaml) and regenerating the router via `fastapi-codegen --input openapi.yaml --output app/generated`.
- Run tests and contract checks with `pytest` (coverage gate at 90%).
- Schemathesis validates the live routes against the OpenAPI contract during the test suite.

## Deployment

The multi-stage Dockerfile builds a Poetry-based image that serves FastAPI with uvicorn. Railway deployments use `/v1/health` for health checks.
