# BlackRoad OS – Public API

`blackroad-os-api` is the typed HTTP surface for BlackRoad OS. It exposes versioned JSON endpoints that Prism Console and other clients use to query health, agents, finance, events, and RoadChain data. This service participates in the shared **"BlackRoad OS - Master Orchestration"** project alongside Operator, Core, Prism, Web, and Infra.

## Core Endpoints
All routes are prefixed with `/api/v1` and return the standard `{ ok, data | error }` envelope.

- `GET /api/v1/health` – API + dependency health summary
- `GET /api/v1/system/overview` – Aggregated system status and recent metrics
- `GET /api/v1/agents` – List agents with optional `status` and `q` filters
- `GET /api/v1/agents/:id` – Agent detail
- `GET /api/v1/finance/snapshot` – Finance/treasury snapshot
- `GET /api/v1/events` – Recent journal-style events with optional filters
- `GET /api/v1/roadchain/blocks` – RoadChain block headers (mocked for now)

## Getting Started
1. Install dependencies:
   ```bash
   npm install
   ```
2. Run in development mode:
   ```bash
   npm run dev
   ```
3. Build and start production bundle:
   ```bash
   npm run build && npm start
   ```

The server listens on `http://localhost:4000` by default or the configured `PORT`.

## Configuration
Environment is centralized in `src/config.ts` via `getConfig()`.

- `NODE_ENV` – `development` | `test` | `production` (default: `development`)
- `PORT` – HTTP port (default: `4000`)
- `OPERATOR_API_BASE_URL` – Base URL for `blackroad-os-operator` (required in production, default: `http://localhost:4100`)
- `ROADCHAIN_BASE_URL` – Optional base for a future RoadChain backend
- `LOG_LEVEL` – Log verbosity (default: `info`)

## Development Notes
- The API is a thin adapter: it shapes responses, validates inputs, and delegates business logic to `blackroad-os-operator` and `blackroad-os-core` when available.
- RoadChain and some finance data are mocked for now; TODO markers indicate where to swap in real upstream calls.
- Responses always follow the `{ ok: boolean; data?; error? }` envelope to keep Prism and other clients stable.
- Requests are validated with Zod via `validateRequest`; invalid params return `{ ok: false, error: { code: "INVALID_REQUEST" } }`.
- Run `npm run generate:openapi` to produce `docs/openapi.generated.json` from the runtime schemas.

## Prompting & Architecture Guide
- See `docs/mega-prompt.md` for the full “Lead Backend Architect” mega prompt that codifies how to analyze, refactor, and document this API.

## Testing
```bash
npm test
```

## Related Repos
- `blackroad-os-operator` – Agent runner and orchestration
- `blackroad-os-core` – Domain primitives and journaling
- `blackroad-os-prism-console` – Operator UI consuming this API
- `blackroad-os-web` – Public web presence
