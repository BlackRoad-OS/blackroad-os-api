# BlackRoad OS API Overview

`blackroad-os-api` is the versioned HTTP gateway for the BlackRoad Operating System. It shapes responses, enforces contracts, and forwards calls to internal services like `blackroad-os-operator` and future RoadChain storage.

## Responsibilities
- Provide typed, stable JSON endpoints for Prism Console and other clients.
- Normalize responses into a consistent `{ ok, data | error }` envelope.
- Delegate business logic to Operator/Core while handling validation and error contracts at the edge.

## Endpoints (v1)
- `GET /api/v1/health` – API + dependency health summary.
- `GET /api/v1/system/overview` – Aggregated status and recent metrics used by the Prism dashboard.
- `GET /api/v1/agents` – List agents with optional `status` and `q` search filters.
- `GET /api/v1/agents/:id` – Agent detail or `AGENT_NOT_FOUND` on 404.
- `GET /api/v1/finance/snapshot` – Treasury/finance snapshot (mocked until Operator wiring is live).
- `GET /api/v1/events` – Recent journal-style events with optional `severity`, `source`, and `limit` filters.
- `GET /api/v1/roadchain/blocks` – RoadChain block headers (mock data until journal backend is exposed).

## Consumers
- **Prism Console** – Dashboard, Agents, Finance, and Events views call these endpoints.
- **Operator/Core** – Act as upstream data sources for health, agents, and finance metrics.
- **Web/Public surfaces** – May use a narrowed subset later.

## Notes
- Environment configuration is centralized in `src/config.ts` (`PORT`, `NODE_ENV`, `OPERATOR_API_BASE_URL`, `ROADCHAIN_BASE_URL`, `LOG_LEVEL`).
- Mock data is clearly marked with TODOs to be replaced by real upstream calls.
- Authentication/rate limiting are intentionally deferred until requirements are defined.
