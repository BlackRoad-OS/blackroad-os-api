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
