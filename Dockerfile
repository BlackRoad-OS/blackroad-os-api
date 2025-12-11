# Builder stage
FROM python:3.11-slim AS builder
ENV POETRY_VERSION=2.2.1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl ca-certificates git && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"
ENV POETRY_VIRTUALENVS_CREATE=false

COPY pyproject.toml poetry.lock README.md ./
RUN poetry install --without dev --no-interaction --no-ansi --no-root
COPY . .
RUN poetry install --without dev --no-interaction --no-ansi

# Runtime stage
FROM python:3.11-slim
ENV PORT=8000
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=info
ENV ENVIRONMENT=production
WORKDIR /app

# Create non-root user for security
RUN groupadd -r blackroad && useradd -r -g blackroad blackroad

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=builder /app ./

# Set proper permissions
RUN chown -R blackroad:blackroad /app

# Switch to non-root user
USER blackroad

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE ${PORT}
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
