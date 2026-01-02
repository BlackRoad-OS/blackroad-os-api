# BlackRoad OS · API Service

`blackroad-os-api` is the core HTTP API surface for BlackRoad OS. It exposes stable, predictable endpoints that other BlackRoad OS services, agents, and clients use to interact with the system.

This service participates in the shared **"BlackRoad OS - Master Orchestration"** project alongside Operator, Core, Prism, Web, and Infra.

## Quickstart

```bash
# Install dependencies
poetry install

# Run development server
poetry run uvicorn app.main:app --reload
# → http://127.0.0.1:8000/health
```

Docker:

```bash
docker build -t blackroad/api:0.1.0 . -f infra/Dockerfile
docker run -e PORT=8000 -p 8000:8000 blackroad/api:0.1.0
```

## Standard Infrastructure Endpoints

These endpoints follow BlackRoad OS service conventions and are available at the root level:

### `GET /health`
**Purpose:** Lightweight liveness check - returns 200 when process is up and routing works.

**Response:**
```json
{
  "status": "ok",
  "uptime": 123.45
}
```

### `GET /ready`
**Purpose:** Readiness check for load balancers - indicates service is ready to accept traffic.

**Response:**
```json
{
  "ready": true,
  "service": "blackroad-os-api"
}
```

### `GET /version`
**Purpose:** Service version, commit, and environment information.

**Response:**
```json
{
  "service": "blackroad-os-api",
  "version": "0.1.0",
  "commit": "abc123",
  "env": "production"
}
```

**Environment Variables:**
- `BR_OS_API_VERSION` - Override version (defaults to package version)
- `BR_OS_API_COMMIT` - Git commit hash (defaults to "UNKNOWN")
- `BR_OS_ENV` - Environment name (defaults to NODE_ENV or "local")

## API Endpoints

All API routes are prefixed with `/v1` and follow the standard `{ ok, data | error }` envelope.

- `GET /v1/health` – API health with dependency status and version info
- `GET /v1/agents` – List available agents (requires API key)
- `GET /v1/packs` – List available agent packs (requires API key)
- `POST /v1/packs/{id}/install` – Install an agent pack (requires API key)

## Configuration

Runtime settings are managed via environment variables and loaded using Pydantic Settings:

### Standard Environment Variables
- `BR_OS_API_VERSION` – Override version (defaults to package version "0.1.0")
- `BR_OS_API_COMMIT` – Git commit hash (falls back to GIT_COMMIT or "UNKNOWN")
- `BR_OS_ENV` – Environment name (falls back to NODE_ENV or "local")

### API Configuration
- `OPERATOR_URL` – Base URL for the operator service (required for agent operations)
- `PACK_INDEX_URL` – URL that returns JSON list of available agent packs
- `API_KEYS` – Comma-separated API keys for authentication
- `PUBLIC_API_KEY` – Additional API key for public access
- `PORT` – HTTP port (default: 8000)

Copy `.env.example` to `.env` for local development configuration.

## Development

### Linting and Formatting
```bash
poetry run ruff check .
poetry run black .
```

### Testing
```bash
poetry run pytest
poetry run pytest --cov=app --cov-report=term-missing
```

### Running the Server
```bash
# Development mode with auto-reload
poetry run uvicorn app.main:app --reload

# Production mode
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The server exposes interactive API docs at `/docs` (Swagger UI) and `/redoc` (ReDoc).

## Architecture

The API is a thin adapter that:
- Shapes responses and validates inputs
- Delegates business logic to `blackroad-os-operator` and `blackroad-os-core`
- Maintains a stable interface for Prism Console and other clients
- Follows the standard `{ ok: boolean, data?: any, error?: { code, message } }` envelope

## Deployment

The service includes:
- Multi-stage Dockerfile in `infra/Dockerfile`
- Railway deployment configuration in `railway.toml`
- Health check endpoints for container orchestration
- Automatic version injection via environment variables

## Trinity System

This repository includes the complete **Light Trinity System**:
- 🔴 **RedLight** – 23 brand templates and design system
- 💚 **GreenLight** – 103 logging templates and multi-agent coordination
- 💛 **YellowLight** – Infrastructure automation and deployment tools

See `.trinity/README.md` for complete documentation.

Trinity compliance is automatically checked via `.github/workflows/trinity-compliance.yml`.

## Contributing

This repository follows BlackRoad OS conventions:
- All commits are signed and attributed
- PRs require passing tests and Trinity compliance
- Code must pass ruff and black formatting checks
- Test coverage must be maintained above 90%

## License

See [LICENSE](./LICENSE) for details.
