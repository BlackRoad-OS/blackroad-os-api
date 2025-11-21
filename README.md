# BlackRoad OS – Public API

Public API gateway for the BlackRoad Operating System. This service exposes common health/info endpoints and versioned API routes that coordinate with core BlackRoad services.

## Endpoints

- `GET /health` – Liveness check
- `GET /info` – Service metadata
- `GET /version` – Version info
- `GET /debug/env` – Safe subset of environment values
- `GET /v1/ping` – Example API endpoint

## Running locally

1. Install dependencies:

   ```bash
   npm install
   ```

2. Start the development server:

   ```bash
   npm run dev
   ```

   The API listens on `http://localhost:8080` by default.

## Build and start

```bash
npm run build
npm start
```

## Environment variables

See `.env.example` for defaults. Key values:

- `OS_ROOT` – Base URL for the BlackRoad OS
- `SERVICE_BASE_URL` – External URL for this public API
- `CORE_BASE_URL` – Core service base URL
- `OPERATOR_BASE_URL` – Operator service base URL
- `LOG_LEVEL` – Logging verbosity
- `PORT` – Port to bind (default `8080`)

## Tests

Run the test suite with:

```bash
npm test
```

## Deployment (Railway)

Railway uses `railway.json`:

- Build: `npm install && npm run build`
- Start: `npm start`
- Healthcheck: `/health` on port `8080`
