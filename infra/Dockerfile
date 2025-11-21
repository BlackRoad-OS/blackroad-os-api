FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY infra/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY schemas/ ./schemas/

# Expose port
EXPOSE 8080

ENV PORT=8080

# Run the application
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
