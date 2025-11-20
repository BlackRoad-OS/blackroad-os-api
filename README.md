# BlackRoad OS — Public API Gateway

FastAPI-powered public gateway that fronts Core and Agents services with versioned routing, thin proxying, and API key enforcement.

## What it does

- Exposes `/health` and `/version` for liveness and build metadata.
- Adds `/v1` routes with API key authentication and consistent error wrapping.
- Proxies requests to upstreams:
  - `/v1/core/*` → `CORE_API_URL`
  - `/v1/agents/*` → `AGENTS_API_URL`

## Configuration

Environment variables are loaded through `app.config.Settings`.

| Variable | Required | Description |
| --- | --- | --- |
| `NODE_ENV` | No (default `development`) | Deployment environment label. |
| `PUBLIC_API_URL` | Yes (non-dev) | External URL for this gateway. |
| `CORE_API_URL` | Yes (non-dev) | Upstream Core backend base URL. |
| `AGENTS_API_URL` | No | Upstream Agents API base URL. |
| `API_KEYS` | Yes (non-dev) | Comma-separated list of API keys authorized for `/v1` routes. |
| `PUBLIC_API_KEY` | Optional | Single API key value if not using `API_KEYS`. |
| `LOG_LEVEL` | No | Application log level (default `info`). |
| `REQUEST_TIMEOUT_MS` | No | Upstream request timeout in milliseconds (default `10000`). |
| `GIT_COMMIT` / `RAILWAY_GIT_COMMIT_SHA` | No | Commit SHA used for `/version`. |
| `BUILD_TIME` | No | Build timestamp used for `/version`. |

## Running locally

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Export a sample API key (either `API_KEYS` or `PUBLIC_API_KEY` works):

   ```bash
   export PUBLIC_API_KEY=local-dev-key
   export CORE_API_URL=http://localhost:9000  # point to your Core service
   export AGENTS_API_URL=http://localhost:9100  # optional
   ```

3. Start the gateway:

   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

## Example requests

Health and version (no API key required):

```bash
curl http://localhost:8000/health
curl http://localhost:8000/version
curl http://localhost:8000/v1/health
```

Proxying upstreams (API key required):

```bash
# Ping Core
curl -H "x-api-key: local-dev-key" http://localhost:8000/v1/core/ping

# Forward any Core path
curl -X POST \
  -H "x-api-key: local-dev-key" \
  -H "Content-Type: application/json" \
  -d '{"hello": "world"}' \
  "http://localhost:8000/v1/core/some/path"

# Forward any Agents path
curl -H "x-api-key: local-dev-key" "http://localhost:8000/v1/agents/demo"
```

## Deployment

- **Railway project**: `blackroad-core`
- **Service name**: `public-api`
- **Build**: `pip install -r requirements.txt`
- **Start**: `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`

GitHub Actions workflow `.github/workflows/api-deploy.yaml` deploys to Railway on `dev`, `staging`, and `main` branches and runs health checks against `/health` and `/v1/health` after each deploy.
