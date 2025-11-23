# BlackRoad OS API Overview

The **blackroad-os-api** service is the public API gateway for the BlackRoad Operating System. It exposes lightweight monitoring endpoints and forwards finance-focused read APIs from the finance agents that live in **blackroad-os-operator**.

## Responsibilities
- Provide health and version endpoints for infrastructure monitoring.
- Surface finance insights (summary, cash forecasts, financial statements) produced by the operator's finance agents.
- Act as the forward-compatible entry point for additional agent/task/compliance APIs.

## Architecture
- **HTTP Server:** Express with centralized middleware for logging and error handling.
- **Operator Client:** `HttpOperatorClient` bridges outbound requests to `blackroad-os-operator` using the configured `OPERATOR_BASE_URL`.
- **Types:** Finance contracts live in `src/types/finance.ts` and mirror GAAP-inspired outputs from the finance agents.

## Authentication & Security
Authentication and authorization are not yet wired. Add API key or JWT validation middleware once requirements are defined. TODOs are in the codebase for rate limiting and structured observability.

## Running Locally
1. Install dependencies: `npm install`
2. Start dev server: `npm run dev`
3. Call endpoints:
   - `GET /health`
   - `GET /version`
   - `GET /finance/summary`
   - `GET /finance/cash-forecast`
   - `GET /finance/statements/{period}` (e.g., `2025-Q1`)

Finance endpoints are read-only views into the operator; any mutations belong in upstream agent services.
