# BlackRoad OS — API Gateway

## Short Description

Unified FastAPI backend for routing, auth, services, and shared API contracts.

## Long Description

API Gateway is the canonical service defining routes, schemas, validation, identity tokens, auth flows, and service-to-service communication. Every other component — Web, Prism, Core, Operator — calls into this.

## Structured Table

| Field          | Value                                   |
| -------------- | --------------------------------------- |
| **Purpose**    | Routing, shared schemas, identity, auth |
| **Depends On** | None (root backend)                     |
| **Used By**    | All components                          |
| **Owner**      | Cece + Alexa                            |
| **Status**     | Active — always evolving                |

## Roadmap Board (API)

Columns:

* **Schema Planning**
* **Routes**
* **Auth**
* **Testing**
* **Deploy**
* **Stable**

Sample tasks:

* /health and version endpoints
* Identity/token lifecycle
* Route coverage expansion
* Agent protocol endpoints
* Pocket OS API handler

---

## Repository overview

This repository implements the BlackRoad public API gateway using FastAPI. It provides:

- `/health` and `/version` liveness + build metadata.
- Versioned `/v1` surface with API key authentication by default.
- Proxy-style routes for core and agents upstreams with shared error handling.
- Consistent configuration via environment variables.

Project structure:

```
app/
  config.py           # Environment-driven settings
  main.py             # FastAPI entrypoint
  errors.py           # Common error helpers
  clients/            # Upstream HTTP clients
  middleware/         # Request ID, auth, and error handling middleware
  routes/             # Root and versioned routers
```

## Environment variables

| Variable | Required | Description |
| --- | --- | --- |
| `NODE_ENV` | No (default `development`) | Deployment environment label. |
| `PUBLIC_API_URL` | Yes (non-dev) | External URL for this gateway. |
| `CORE_API_URL` | Yes (non-dev) | Upstream Core backend base URL. |
| `AGENTS_API_URL` | No | Upstream Agents API base URL. |
| `API_KEYS` | Yes (non-dev) | Comma-separated list of API keys authorized for `/v1` routes. |
| `LOG_LEVEL` | No | Application log level (default `info`). |
| `REQUEST_TIMEOUT_MS` | No | Default upstream request timeout in milliseconds (default `10000`). |
| `GIT_COMMIT` / `RAILWAY_GIT_COMMIT_SHA` | No | Commit SHA used for `/version`. |
| `BUILD_TIME` | No | Build timestamp used for `/version`. |

## Railway deployment

- **Railway project**: `blackroad-core`
- **Service name**: `public-api`

### Commands

- **Build**: `pip install -r requirements.txt`
- **Start**: `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`

### Environment mappings

- **dev**
  - `PUBLIC_API_URL` = dev Railway URL or `https://dev.api.blackroad.systems`
  - `CORE_API_URL` = core dev Railway URL
  - `AGENTS_API_URL` = agents dev Railway URL
- **staging**
  - `PUBLIC_API_URL` = `https://staging.api.blackroad.systems`
  - `CORE_API_URL` = `https://staging.core.blackroad.systems`
  - `AGENTS_API_URL` = `https://staging.agents.blackroad.systems`
- **prod**
  - `PUBLIC_API_URL` = `https://api.blackroad.systems`
  - `CORE_API_URL` = `https://core.blackroad.systems`
  - `AGENTS_API_URL` = `https://agents.blackroad.systems`

### DNS (Cloudflare)

- `api.blackroad.systems` → CNAME `public-api-prod.up.railway.app` (proxied)
- `staging.api.blackroad.systems` → CNAME `public-api-staging.up.railway.app` (proxied)
- `dev.api.blackroad.systems` → CNAME `public-api-dev.up.railway.app` (proxied)

### CI/CD

GitHub Actions workflow `.github/workflows/deploy-api.yml` deploys to Railway:

- `dev` branch → Railway `dev`
- `staging` branch → Railway `staging`
- `main` branch → Railway `prod`

After deployment, the workflow runs health checks against `/health` and `/v1/health`.
