# BlackRoad OS API - Development Makefile

.PHONY: help install dev test lint health version clean codegen docker-build docker-run

PORT := 8000

help:
	@echo "BlackRoad OS API - Development Commands"
	@echo ""
	@echo "  make install    - Install dependencies with Poetry"
	@echo "  make dev        - Run development server"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linter"
	@echo "  make health     - Check health endpoint"
	@echo "  make version    - Check version endpoint"
	@echo "  make codegen    - Generate code from OpenAPI spec"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"
	@echo ""

install:
	poetry install

dev:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port $${PORT:-$(PORT)}

test:
	poetry run pytest

lint:
	poetry run ruff check app/

health:
	@curl -sf http://localhost:$(PORT)/health | python3 -m json.tool || echo "Service not running on port $(PORT)"

version:
	@curl -sf http://localhost:$(PORT)/version | python3 -m json.tool || echo "Service not running on port $(PORT)"

codegen:
	poetry run fastapi-codegen --input openapi.yaml --output app/generated

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

docker-build:
	docker build -t blackroad-os-api .

docker-run:
	docker run -p $(PORT):$(PORT) -e PORT=$(PORT) blackroad-os-api
