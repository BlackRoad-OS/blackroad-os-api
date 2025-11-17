# BlackRoad OS API

A minimal FastAPI service for BlackRoad OS with health and version endpoints.

## Project Structure

```
.
├── app/              # FastAPI application
│   ├── __init__.py   # Package initialization with version
│   └── main.py       # Main application with /health and /version endpoints
├── schemas/          # Pydantic models for requests/responses
│   ├── __init__.py
│   └── responses.py  # Response models
└── infra/            # Infrastructure and deployment files
    ├── Dockerfile    # Docker container configuration
    ├── requirements.txt  # Python dependencies
    └── railway.toml  # Railway.app deployment configuration
```

## Getting Started

### Local Development

1. Install dependencies:
```bash
pip install -r infra/requirements.txt
```

2. Run the server:
```bash
uvicorn app.main:app --reload
```

3. Access the API:
- Health check: http://localhost:8000/health
- Version: http://localhost:8000/version
- API docs: http://localhost:8000/docs

### Docker

Build and run with Docker:
```bash
docker build -f infra/Dockerfile -t blackroad-os-api .
docker run -p 8000:8000 blackroad-os-api
```

### Deploy to Railway

This project includes a `railway.toml` configuration file for easy deployment to Railway.app.

## API Endpoints

- `GET /health` - Health check endpoint returning `{"status": "ok"}`
- `GET /version` - Version endpoint returning `{"version": "0.1.0"}`
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)
