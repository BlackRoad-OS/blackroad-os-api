# BlackRoad OS – Public API

Public API gateway for the BlackRoad Operating System. This service fronts the platform's public-facing endpoints and relays metadata about the OS ecosystem services.

## Overview
- **Service Name:** BlackRoad OS – Public API
- **Service ID:** `api`
- **Base URL:** https://api.blackroad.systems
- **Default Port:** 8080

## Endpoints
- `GET /health` – Liveness check returning service id and timestamp.
- `GET /info` – Service metadata including base URL, OS root, and version.
- `GET /version` – Service id and version from `package.json`.
- `GET /debug/env` – Safe subset of environment configuration.
- `GET /v1/health` – Versioned health check endpoint.
- `GET /v1/ping` – Versioned ping endpoint for API consumers.

## Getting Started
1. Install dependencies
   ```bash
   npm install
   ```
2. Run in development mode (with live reload)
   ```bash
   npm run dev
   ```
3. Build for production
   ```bash
   npm run build
   ```
4. Start the compiled server
   ```bash
   npm start
   ```

The server listens on `http://localhost:8080` by default or `PORT` if provided.

## Environment Variables
See `.env.example` for defaults:
- `OS_ROOT` – Base URL for the BlackRoad OS
- `SERVICE_BASE_URL` – External URL for this public API
- `CORE_BASE_URL` – Core service base URL
- `OPERATOR_BASE_URL` – Operator service base URL
- `LOG_LEVEL` – Logging verbosity
- `PORT` – Port to bind (default `8080`)

## Railway Deployment
The repository is configured for Railway deployment using the modern 2024 format:

**Configuration Files:**
- `railway.json` - Railway deployment configuration with schema validation
- `nixpacks.toml` - Explicit build configuration for Node.js 20

**Deployment Settings:**
- Builder: Nixpacks
- Build: `npm install && npm run build`
- Start: `npm start`
- Healthcheck: `/health` (timeout: 100s)
- Restart Policy: Always

The service will automatically deploy to Railway when changes are pushed to the configured branches (dev, staging, main).

## Testing
Run the test suite with:
```bash
npm test
```
