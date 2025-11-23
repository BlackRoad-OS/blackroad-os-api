# BlackRoad OS – Public API

Public API gateway for the BlackRoad Operating System. This service exposes health/version endpoints for monitoring and proxies finance data from the Automated Finance Layer in **blackroad-os-operator**.

## Features
- **Health & Version** endpoints for observability.
- **Finance** endpoints for summaries, cash forecasts, and financial statements.
- Structured, testable Express setup with centralized middleware.

## Getting Started
1. Install dependencies:
   ```bash
   npm install
   ```
2. Run in development mode:
   ```bash
   npm run dev
   ```
3. Build for production:
   ```bash
   npm run build
   ```
4. Start the compiled server:
   ```bash
   npm start
   ```

The server listens on `http://localhost:3001` by default or the configured `PORT`.

## Configuration
Set the following environment variables as needed:
- `PORT` – Port to bind (default `3001`)
- `LOG_LEVEL` – Logging verbosity (default `info`)
- `OPERATOR_BASE_URL` – Base URL for `blackroad-os-operator`
- `REQUEST_TIMEOUT_MS` – Timeout for upstream requests (default `5000`)

## Example Requests
```bash
curl http://localhost:3001/health
curl http://localhost:3001/finance/summary
curl http://localhost:3001/finance/statements/2025-Q1
```

## Testing
Run the test suite with:
```bash
npm test
```

## Docs
- [API overview](docs/api-overview.md)
- [OpenAPI spec](docs/openapi.yaml)

## TODO
- Add authentication and authorization.
- Add rate limiting and abuse protection.
- Improve structured logging and metrics.
