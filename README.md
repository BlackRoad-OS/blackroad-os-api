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
