# BlackRoad OS Infrastructure Bible

**Version:** 1.0.0  
**Last Updated:** December 12, 2025  
**Author:** Alexa Louise Amundson (Cecilia)  
**Organization:** BlackRoad OS, Inc.

-----

## Table of Contents

1. [Philosophy: Why This Architecture](#philosophy-why-this-architecture)
1. [The Three Layers](#the-three-layers)
1. [Hardware Inventory](#hardware-inventory)
1. [Service Inventory](#service-inventory)
1. [Network Architecture](#network-architecture)
1. [Cloudflare Setup](#cloudflare-setup)
1. [Tailscale Mesh Network](#tailscale-mesh-network)
1. [Docker & Containers](#docker--containers)
1. [Deployment Pipeline](#deployment-pipeline)
1. [Domain Routing](#domain-routing)
1. [Failover Strategy](#failover-strategy)
1. [Local LLM Infrastructure](#local-llm-infrastructure)
1. [API Integration Layer](#api-integration-layer)
1. [Security Model](#security-model)
1. [Monitoring & Logging](#monitoring--logging)
1. [Cost Analysis](#cost-analysis)
1. [Setup Checklist](#setup-checklist)
1. [Troubleshooting](#troubleshooting)

-----

## Philosophy: Why This Architecture

### The Problem with Traditional Cloud

Traditional cloud architecture (AWS, GCP, Azure) solves problems that most individual builders and small teams don’t have:

- 99.99% uptime SLAs (you need 99% for real users)
- Infinite horizontal scaling (you need to handle 1,000-10,000 users)
- Enterprise compliance (you need basic security)
- Someone to sue when it breaks (you need it to just work)

The result is:

- $500-5,000+/month in cloud bills
- Vendor lock-in across 47 services
- Complexity that requires a DevOps team
- Your data living on someone else’s computers

### The BlackRoad Approach

```
YOU OWN THE COMPUTE.
THE CLOUD IS JUST ROUTING.
```

This architecture is built on three principles:

1. **Sovereignty**: Your hardware, your data, your control
1. **Simplicity**: Minimum viable infrastructure, maximum capability
1. **Economics**: One-time hardware costs + ~$50/month operational

### What This Enables

- Run local LLMs without per-token costs
- Keep sensitive data on your own network
- Full control over the entire stack
- No surprise cloud bills
- Actual understanding of what’s running and why

-----

## The Three Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                        LAYER 3: YOU BUILD                        │
│                                                                  │
│   Lucidia Core │ Agent Orchestration │ Memory Systems │ UI/API  │
│                                                                  │
│   This is what only YOU can build. The 1,000 agents. The        │
│   Z-framework. The paraconsistent logic. The recursive AI.      │
├─────────────────────────────────────────────────────────────────┤
│                     LAYER 2: SERVICES VIA API                    │
│                                                                  │
│   Stripe │ Canva │ HuggingFace │ Google Drive │ Ollama │ Qwen   │
│                                                                  │
│   Don't rebuild these. Just call them. They've spent millions   │
│   making payment rails, model hosting, design tools work.       │
├─────────────────────────────────────────────────────────────────┤
│                      LAYER 1: INFRASTRUCTURE                     │
│                                                                  │
│   Cloudflare (Edge) → Your Hardware (Compute) → Droplet (Backup)│
│                                                                  │
│   This document is primarily about this layer.                  │
└─────────────────────────────────────────────────────────────────┘
```

-----

## Hardware Inventory

### Current Fleet

|Device              |Hostname          |Role                    |Specs                  |IP (Tailscale)|
|--------------------|------------------|------------------------|-----------------------|--------------|
|Raspberry Pi 5 #1   |`pi5-alpha`       |Agent Pool / API Gateway|Quad A76, 8GB          |`100.x.x.1`   |
|Raspberry Pi 5 #2   |`pi5-beta`        |Agent Pool              |Quad A76, 8GB          |`100.x.x.2`   |
|Raspberry Pi 5 #3   |`pi5-gamma`       |Database / State        |Quad A76, 8GB          |`100.x.x.3`   |
|Raspberry Pi 400    |`pi400-delta`     |Monitoring / Logs       |Quad A72, 4GB          |`100.x.x.4`   |
|Raspberry Pi Zero   |`pi0-epsilon`     |Health Checks Only      |Single A53, 512MB      |`100.x.x.5`   |
|Jetson Orin Nano    |`jetson-prime`    |LLM Inference           |6-core + 1024 CUDA, 8GB|`100.x.x.10`  |
|DigitalOcean Droplet|`droplet-failover`|Backup / Failover       |1 vCPU, 1GB            |`100.x.x.100` |

### Role Definitions

**Agent Pool (Pi 5s)**

- Runs containerized agent instances
- Handles HTTP API requests
- Manages WebSocket connections
- Executes orchestration logic

**LLM Inference (Jetson)**

- Runs vLLM or llama.cpp
- Serves model inference requests
- Handles embedding generation
- ONLY device that runs actual AI models

**Database/State (Pi 5 #3)**

- PostgreSQL or SQLite
- Milvus vector database
- Append-only memory journals
- State persistence

**Monitoring (Pi 400)**

- Prometheus metrics collection
- Grafana dashboards
- Log aggregation
- Health check orchestration

**Failover (Droplet)**

- Minimal API that returns “system down for maintenance”
- SSH jump host when home network is unreachable
- Backup cloudflared tunnel endpoint

-----

## Service Inventory

### Cloudflare (Current State)

**Workers (59 total - NEEDS CLEANUP)**

Core Workers to KEEP:

- `blackroad-edge-gateway` - Main entry point, routes all traffic
- `blackroad-api-gateway` - API routing and auth
- `blackroad-auth` - Authentication/identity
- `blackroad-router` - Domain-based routing
- `lucidia-core` - Lucidia system entry point
- `cece` - Cecilia agent interface

Workers to EVALUATE:

- `blackroad-billing`, `blackroad-stripe-*` - Consolidate into one
- `blackroad-*-router` (7 different routers) - Consolidate
- Various templates and tests - DELETE

**KV Namespaces (16 total)**

Essential:

- `API_KEYS` - API key storage
- `API_KEY_METADATA` - Key metadata
- `IDENTITIES` - User/agent identities
- `RATE_LIMITS` / `RATE_LIMIT` - Rate limiting (consolidate these)
- `CACHE` - General caching
- `BILLING` - Billing state

Evaluate/Consolidate:

- `blackroad-router-*` namespaces
- `blackroad-api-*` namespaces
- `TELEMETRY_KV`

**D1 Databases (4 total)**

- `blackroad-os-main` - Primary database
- `blackroad-logs` - Log storage
- `blackroad-d1-database` - Generic (evaluate purpose)
- `openapi-template-db` - DELETE (template artifact)

**R2 Buckets (6 total)**

- `blackroad-os-core-storage` - Core system files
- `blackroad-os-agents-storage` - Agent data/state
- `blackroad-os-api-storage` - API artifacts
- `blackroad-os-api-gateway-storage` - Gateway config
- `blackroad-os-mesh-storage` - Mesh network data
- `lucidia-core-storage` - Lucidia system files

-----

## Network Architecture

### The Traffic Flow

```
                         INTERNET
                            │
                            ▼
                    ┌───────────────┐
                    │  CLOUDFLARE   │
                    │   (DNS/CDN)   │
                    └───────┬───────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
            ▼                               ▼
    ┌───────────────┐               ┌───────────────┐
    │   WORKERS     │               │   TUNNELS     │
    │ (Edge Logic)  │               │ (To Hardware) │
    └───────┬───────┘               └───────┬───────┘
            │                               │
            │   ┌───────────────────────────┘
            │   │
            ▼   ▼
    ┌─────────────────────────────────────────────────┐
    │              TAILSCALE MESH                      │
    │                                                  │
    │  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
    │  │  Pi 5   │──│  Pi 5   │──│  Pi 5   │         │
    │  │ (alpha) │  │ (beta)  │  │ (gamma) │         │
    │  └────┬────┘  └────┬────┘  └────┬────┘         │
    │       │            │            │               │
    │       └────────────┼────────────┘               │
    │                    │                            │
    │              ┌─────┴─────┐                      │
    │              │  JETSON   │                      │
    │              │  (LLM)    │                      │
    │              └───────────┘                      │
    │                                                  │
    │  ┌─────────┐              ┌─────────────────┐   │
    │  │ Pi 400  │              │ DO Droplet      │   │
    │  │ (mon)   │              │ (failover)      │   │
    │  └─────────┘              └─────────────────┘   │
    └─────────────────────────────────────────────────┘
```

### Why This Design

1. **Cloudflare Workers** handle edge logic (routing, auth, rate limiting) at 200+ global edge locations
1. **Cloudflare Tunnels** create secure outbound connections from your hardware (no open ports, no static IP needed)
1. **Tailscale** creates a private mesh between all your devices regardless of physical location
1. **Your Hardware** does the actual compute work
1. **Droplet** is the escape hatch when your home network fails

-----

## Cloudflare Setup

### Step 1: Domain Configuration

For each domain (blackroad.io, lucidia.earth, etc.):

1. Buy domain from registrar (GoDaddy, Namecheap, etc.)
1. Change nameservers to Cloudflare:
   
   ```
   ns1.cloudflare.com
   ns2.cloudflare.com
   ```
1. Wait for propagation (usually 10-60 minutes)
1. Domain now managed by Cloudflare

### Step 2: DNS Records

Basic DNS setup for a domain pointing to your tunnel:

```
Type    Name        Content                         Proxy
────────────────────────────────────────────────────────────
CNAME   @           <tunnel-id>.cfargotunnel.com    Proxied
CNAME   www         <tunnel-id>.cfargotunnel.com    Proxied
CNAME   api         <tunnel-id>.cfargotunnel.com    Proxied
CNAME   agents      <tunnel-id>.cfargotunnel.com    Proxied
```

The tunnel ID comes from Step 3.

### Step 3: Tunnel Setup

**On each Pi/Jetson, install cloudflared:**

```bash
# For Raspberry Pi (ARM64)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# Login to Cloudflare
cloudflared tunnel login
# This opens a browser - authenticate with your Cloudflare account

# Create a tunnel
cloudflared tunnel create pi5-alpha
# This outputs a tunnel ID and creates credentials file

# Note the tunnel ID (e.g., a]1234abcd-5678-efgh-9012-ijklmnop3456)
```

**Create tunnel config:**

```yaml
# /home/pi/.cloudflared/config.yml

tunnel: <your-tunnel-id>
credentials-file: /home/pi/.cloudflared/<tunnel-id>.json

ingress:
  # API requests go to local API server
  - hostname: api.blackroad.io
    service: http://localhost:8000
  
  # Agent requests go to agent pool
  - hostname: agents.blackroad.io
    service: http://localhost:8001
  
  # Main website
  - hostname: blackroad.io
    service: http://localhost:3000
  
  # Catch-all (required)
  - service: http_status:404
```

**Run the tunnel:**

```bash
# Test it first
cloudflared tunnel run pi5-alpha

# Then install as service
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

### Step 4: Workers (Simplified)

Instead of 59 workers, you need approximately 5:

**1. Edge Gateway (`blackroad-edge-gateway`)**

```javascript
// Routes all incoming requests to appropriate backend
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const hostname = url.hostname;
    
    // Route based on domain
    const routes = {
      'api.blackroad.io': 'https://pi5-alpha.tail<xxxxx>.ts.net:8000',
      'agents.blackroad.io': 'https://pi5-beta.tailxxxxx.ts.net:8001',
      'llm.blackroad.io': 'https://jetson-prime.tailxxxxx.ts.net:8080',
    };
    
    const backend = routes[hostname];
    if (backend) {
      return fetch(backend + url.pathname + url.search, request);
    }
    
    return new Response('Not Found', { status: 404 });
  }
}
```

**2. Auth Gateway (`blackroad-auth`)**

```javascript
// Validates API keys and JWT tokens
export default {
  async fetch(request, env) {
    const apiKey = request.headers.get('X-API-Key');
    
    if (!apiKey) {
      return new Response('Unauthorized', { status: 401 });
    }
    
    // Check API key in KV
    const keyData = await env.API_KEYS.get(apiKey);
    if (!keyData) {
      return new Response('Invalid API Key', { status: 403 });
    }
    
    // Add user info to request headers and forward
    const newRequest = new Request(request);
    newRequest.headers.set('X-User-ID', JSON.parse(keyData).userId);
    
    return fetch(newRequest);
  }
}
```

**3. Rate Limiter (`blackroad-ratelimit`)**

```javascript
// Rate limits by API key
export default {
  async fetch(request, env) {
    const apiKey = request.headers.get('X-API-Key') || 'anonymous';
    const key = `rate:${apiKey}:${Math.floor(Date.now() / 60000)}`;
    
    const current = parseInt(await env.RATE_LIMITS.get(key) || '0');
    const limit = 100; // 100 requests per minute
    
    if (current >= limit) {
      return new Response('Rate Limited', { status: 429 });
    }
    
    await env.RATE_LIMITS.put(key, String(current + 1), { expirationTtl: 120 });
    
    return fetch(request);
  }
}
```

**4. Billing/Stripe (`blackroad-billing`)**

```javascript
// Handles all Stripe webhooks and billing logic
// Consolidate blackroad-stripe-billing, blackroad-stripe-webhooks, blackroad-stripe-checkout
```

**5. Telemetry (`blackroad-telemetry`)**

```javascript
// Collects and forwards logs/metrics
```

### Step 5: KV Cleanup

Consolidate to these namespaces:

|Namespace   |Purpose                                 |
|------------|----------------------------------------|
|`AUTH`      |API keys, tokens, sessions              |
|`IDENTITY`  |User and agent identities               |
|`RATE_LIMIT`|Rate limiting counters                  |
|`CACHE`     |General response caching                |
|`BILLING`   |Billing state and subscription info     |
|`STATE`     |Application state that needs edge access|

-----

## Tailscale Mesh Network

### Why Tailscale

- Creates encrypted WireGuard tunnels between all devices
- Works through NAT, firewalls, carrier-grade NAT
- No open ports required
- Devices get stable IPs (100.x.x.x range)
- Free for up to 100 devices

### Setup on Each Device

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Connect to your network
sudo tailscale up

# First time: authenticate via URL
# This adds the device to your tailnet
```

### Tailscale ACLs

In your Tailscale admin console, set up ACLs:

```json
{
  "acls": [
    // Allow all devices to talk to each other
    {"action": "accept", "src": ["*"], "dst": ["*:*"]},
  ],
  "tagOwners": {
    "tag:server": ["autogroup:admin"],
    "tag:infra": ["autogroup:admin"],
  }
}
```

### Device Naming

After setup, each device gets a Tailscale hostname:

```
pi5-alpha.tailXXXXX.ts.net
pi5-beta.tailXXXXX.ts.net
jetson-prime.tailXXXXX.ts.net
droplet-failover.tailXXXXX.ts.net
```

These hostnames work from anywhere in your tailnet, even if the devices are in different physical locations.

-----

## Docker & Containers

### Why Docker

- “It works on my machine” → “It works everywhere”
- Identical environments across Pi, Jetson, Droplet
- Easy rollback (just run previous image)
- Clean separation of concerns

### Base Dockerfile for Services

```dockerfile
# Dockerfile.base
FROM python:3.11-slim

WORKDIR /app

# Install common dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Multi-Architecture Builds

Your devices have different architectures:

- Pi 5, Pi 400, Pi Zero: ARM64
- Jetson: ARM64 (but with CUDA)
- Droplet: AMD64

Build for multiple architectures:

```bash
# Enable buildx
docker buildx create --use

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/blackroad-os/api:latest \
  --push .
```

### Docker Compose for Local Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/blackroad
      - JETSON_URL=http://jetson-prime.tailXXXXX.ts.net:8080
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=blackroad
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

-----

## Deployment Pipeline

### The Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   CODE       │────▶│    BUILD     │────▶│   DEPLOY     │
│              │     │              │     │              │
│ - Cursor     │     │ - GitHub     │     │ - Pi pulls   │
│ - Pyto       │     │   Actions    │     │   new image  │
│ - Working    │     │ - Docker     │     │ - Restart    │
│   Copy       │     │   buildx     │     │   container  │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │
       │                    │                    │
       ▼                    ▼                    ▼
    git push          Build image          Watchtower OR
    to main           Push to GHCR         SSH + docker pull
```

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Pi
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: pi5-alpha.tailXXXXX.ts.net
          username: pi
          key: ${{ secrets.PI_SSH_KEY }}
          script: |
            docker pull ghcr.io/${{ github.repository }}:latest
            docker stop api || true
            docker rm api || true
            docker run -d --name api \
              -p 8000:8000 \
              --restart unless-stopped \
              ghcr.io/${{ github.repository }}:latest
```

### Alternative: Watchtower (Auto-Update)

Run Watchtower on each Pi to automatically pull new images:

```bash
docker run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  --interval 300 \
  --cleanup
```

This checks for new images every 5 minutes and auto-updates.

### Manual Deployment (Emergency/Phone)

From Shellfish or any SSH client:

```bash
# SSH to Pi via Tailscale
ssh pi@pi5-alpha.tailXXXXX.ts.net

# Pull latest and restart
docker pull ghcr.io/blackroad-os/api:latest
docker-compose down
docker-compose up -d
```

-----

## Domain Routing

### Domain Map

|Domain             |Purpose                 |Routes To             |
|-------------------|------------------------|----------------------|
|blackroad.io       |Main company site       |Pi 5 Alpha (port 3000)|
|api.blackroad.io   |Public API              |Pi 5 Alpha (port 8000)|
|agents.blackroad.io|Agent interactions      |Pi 5 Beta (port 8001) |
|lucidia.earth      |Lucidia platform        |Pi 5 Alpha (port 3001)|
|llm.blackroad.io   |LLM inference (internal)|Jetson (port 8080)    |
|status.blackroad.io|Status page             |Cloudflare Worker     |

### Cloudflare Tunnel Config (Combined)

```yaml
# /home/pi/.cloudflared/config.yml on Pi 5 Alpha

tunnel: <tunnel-id>
credentials-file: /home/pi/.cloudflared/<tunnel-id>.json

ingress:
  # Main site
  - hostname: blackroad.io
    service: http://localhost:3000
  - hostname: www.blackroad.io
    service: http://localhost:3000
  
  # API
  - hostname: api.blackroad.io
    service: http://localhost:8000
  
  # Lucidia
  - hostname: lucidia.earth
    service: http://localhost:3001
  - hostname: www.lucidia.earth
    service: http://localhost:3001
  
  # Internal routing via Tailscale
  - hostname: agents.blackroad.io
    service: http://pi5-beta.tailXXXXX.ts.net:8001
  
  - hostname: llm.blackroad.io
    service: http://jetson-prime.tailXXXXX.ts.net:8080
  
  # Catch-all
  - service: http_status:404
```

-----

## Failover Strategy

### When Home Internet Dies

1. Cloudflare detects tunnel is down (within 30 seconds)
1. Traffic fails over to Droplet tunnel
1. Droplet serves maintenance page OR proxies to cached responses

### Droplet Setup

```bash
# On your DigitalOcean droplet

# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# Create failover tunnel
cloudflared tunnel login
cloudflared tunnel create droplet-failover

# Config
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: <failover-tunnel-id>
credentials-file: /home/user/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: "*.blackroad.io"
    service: http://localhost:8080
  - hostname: "*.lucidia.earth"
    service: http://localhost:8080
  - service: http_status:404
EOF

# Simple failover server
cat > failover.py << 'EOF'
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/{path:path}")
async def failover(path: str):
    return HTMLResponse("""
    <html>
    <body style="font-family: system-ui; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #111; color: #fff;">
        <div style="text-align: center;">
            <h1>BlackRoad OS</h1>
            <p>Systems temporarily offline. Back shortly.</p>
            <p style="opacity: 0.5;">Failover active.</p>
        </div>
    </body>
    </html>
    """)
EOF

# Run it
pip install fastapi uvicorn
uvicorn failover:app --host 0.0.0.0 --port 8080 &

# Start tunnel
cloudflared tunnel run droplet-failover
```

### Cloudflare Load Balancing (Optional)

For automatic failover, use Cloudflare Load Balancing ($5/month):

1. Create a Load Balancer in Cloudflare dashboard
1. Add two origins:
- Primary: Your Pi tunnel
- Backup: Droplet tunnel
1. Set health checks (HTTP GET to /health endpoint)
1. Cloudflare automatically routes around failures

-----

## Local LLM Infrastructure

### Jetson Orin Nano Setup

```bash
# On Jetson

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Pull and run vLLM
docker run --runtime nvidia --gpus all \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -p 8080:8000 \
  --restart unless-stopped \
  vllm/vllm-openai:latest \
  --model Qwen/Qwen2.5-7B-Instruct \
  --max-model-len 4096
```

### Alternative: Ollama (Simpler)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull qwen2.5:7b

# Run server
ollama serve
# Listens on localhost:11434

# API compatible with OpenAI
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5:7b",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Calling LLM from Pi

```python
# On Pi, calling Jetson for inference

import httpx

JETSON_URL = "http://jetson-prime.tailXXXXX.ts.net:8080"

async def get_completion(prompt: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{JETSON_URL}/v1/chat/completions",
            json={
                "model": "qwen2.5:7b",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
            },
            timeout=60.0,
        )
        return response.json()["choices"][0]["message"]["content"]
```

-----

## API Integration Layer

### Services You Call (Don’t Rebuild)

|Service     |Purpose         |Integration          |
|------------|----------------|---------------------|
|Stripe      |Payments        |Webhook + API        |
|Canva       |Design assets   |REST API             |
|HuggingFace |Models, datasets|Hub API              |
|Google Drive|Document storage|OAuth + API          |
|Ollama/vLLM |Local LLM       |OpenAI-compatible API|

### Environment Variables Pattern

```bash
# .env (never commit this)
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
CANVA_API_KEY=xxx
HUGGINGFACE_TOKEN=hf_xxx
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
JETSON_URL=http://jetson-prime.tailXXXXX.ts.net:8080
DATABASE_URL=postgresql://...
```

### Centralized API Client

```python
# blackroad/integrations/__init__.py

import os
import httpx
from functools import lru_cache

class Integrations:
    def __init__(self):
        self.stripe_key = os.environ["STRIPE_SECRET_KEY"]
        self.hf_token = os.environ["HUGGINGFACE_TOKEN"]
        self.jetson_url = os.environ["JETSON_URL"]
    
    @property
    @lru_cache
    def stripe(self):
        import stripe
        stripe.api_key = self.stripe_key
        return stripe
    
    async def llm_completion(self, messages: list) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.jetson_url}/v1/chat/completions",
                json={"model": "qwen2.5:7b", "messages": messages},
                timeout=60.0,
            )
            return response.json()["choices"][0]["message"]["content"]

# Singleton
integrations = Integrations()
```

-----

## Security Model

### Layers of Security

```
┌─────────────────────────────────────────────────────────┐
│ LAYER 1: Cloudflare                                     │
│ - DDoS protection                                       │
│ - WAF (Web Application Firewall)                        │
│ - Bot management                                        │
│ - SSL termination                                       │
├─────────────────────────────────────────────────────────┤
│ LAYER 2: Cloudflare Workers                             │
│ - API key validation                                    │
│ - Rate limiting                                         │
│ - Request sanitization                                  │
├─────────────────────────────────────────────────────────┤
│ LAYER 3: Tailscale                                      │
│ - All inter-device traffic encrypted (WireGuard)        │
│ - Only authenticated devices can join network           │
│ - No open ports on any device                           │
├─────────────────────────────────────────────────────────┤
│ LAYER 4: Application                                    │
│ - JWT/session validation                                │
│ - Input validation                                      │
│ - Parameterized queries                                 │
└─────────────────────────────────────────────────────────┘
```

### No Open Ports

Your Pis and Jetson should have NO ports open to the internet:

```bash
# Check what's listening
sudo netstat -tlnp

# Should see things bound to:
# - 127.0.0.1:xxxx (localhost only)
# - 100.x.x.x:xxxx (Tailscale only)

# NOT 0.0.0.0:xxxx (that's open to all)
```

Cloudflare Tunnel handles all inbound traffic. Tailscale handles internal mesh. Nothing else needs to be exposed.

### API Key Management

```python
# Generate API keys
import secrets
import hashlib

def generate_api_key() -> tuple[str, str]:
    """Returns (key_to_give_user, hash_to_store)"""
    key = f"br_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    return key, key_hash

def verify_api_key(key: str, stored_hash: str) -> bool:
    return hashlib.sha256(key.encode()).hexdigest() == stored_hash
```

-----

## Monitoring & Logging

### Stack

- **Prometheus**: Metrics collection
- **Grafana**: Dashboards
- **Loki**: Log aggregation (or just CloudFlare Logs)

### Simple Health Check Endpoint

Every service should have:

```python
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": os.environ.get("GIT_SHA", "unknown"),
    }
```

### Pi 400 Monitoring Setup

```yaml
# docker-compose.monitoring.yml on Pi 400

version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  prometheus_data:
  grafana_data:
```

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'pi5-alpha'
    static_configs:
      - targets: ['pi5-alpha.tailXXXXX.ts.net:8000']
  
  - job_name: 'pi5-beta'
    static_configs:
      - targets: ['pi5-beta.tailXXXXX.ts.net:8001']
  
  - job_name: 'jetson'
    static_configs:
      - targets: ['jetson-prime.tailXXXXX.ts.net:8080']
```

-----

## Cost Analysis

### Monthly Operational Costs

|Item                                       |Cost             |
|-------------------------------------------|-----------------|
|Cloudflare Free Tier                       |$0               |
|Cloudflare Pro (optional, better analytics)|$20              |
|DigitalOcean Droplet (1GB)                 |$6               |
|Domains (17 × $12/year ÷ 12)               |~$17             |
|Electricity (Pis + Jetson, ~50W total)     |~$10-15          |
|**Total (Free Tier)**                      |**~$33-38/month**|
|**Total (Pro)**                            |**~$53-58/month**|

### One-Time Hardware Costs (Already Paid)

|Item                   |Cost     |
|-----------------------|---------|
|3× Raspberry Pi 5 (8GB)|~$240    |
|Pi 400                 |~$70     |
|Pi Zero                |~$15     |
|Jetson Orin Nano       |~$500    |
|SD Cards, Cases, Power |~$100    |
|**Total**              |**~$925**|

### Comparison: Cloud-Only Approach

|Item                    |Monthly Cost      |
|------------------------|------------------|
|Vercel Pro              |$20               |
|Railway                 |$20-50            |
|GPU Cloud (RunPod, etc.)|$100-500          |
|Managed Database        |$15-50            |
|**Total**               |**$155-620/month**|

**Break-even**: Your hardware pays for itself in 2-6 months.

-----

## Setup Checklist

### Phase 1: Foundation (Do This Week)

- [ ] Install Tailscale on all devices
- [ ] Verify all devices can ping each other via Tailscale
- [ ] Install cloudflared on Pi 5 Alpha
- [ ] Create first tunnel pointing to Pi 5 Alpha
- [ ] Point blackroad.io DNS to tunnel
- [ ] Verify blackroad.io loads something from Pi

### Phase 2: Services (Do Next Week)

- [ ] Set up Docker on all Pis
- [ ] Create base Dockerfile for services
- [ ] Set up GitHub Actions for one repo
- [ ] Deploy first containerized service
- [ ] Set up cloudflared on Jetson
- [ ] Verify LLM inference works via Tailscale

### Phase 3: Hardening (Do Week 3)

- [ ] Set up Droplet failover tunnel
- [ ] Configure Cloudflare WAF rules
- [ ] Set up API key management in KV
- [ ] Configure rate limiting
- [ ] Set up monitoring on Pi 400

### Phase 4: Cleanup (Do Week 4)

- [ ] Delete unused Cloudflare Workers (target: 5-10 workers max)
- [ ] Consolidate KV namespaces (target: 6 max)
- [ ] Document all running services
- [ ] Create runbook for common operations

-----

## Troubleshooting

### Tunnel Not Connecting

```bash
# Check tunnel status
cloudflared tunnel info <tunnel-name>

# Check if cloudflared is running
systemctl status cloudflared

# View logs
journalctl -u cloudflared -f

# Common fix: re-authenticate
cloudflared tunnel login
```

### Device Not in Tailscale

```bash
# Check Tailscale status
tailscale status

# Re-authenticate
sudo tailscale up --reset

# Check if Tailscale daemon is running
systemctl status tailscaled
```

### Container Won’t Start

```bash
# Check logs
docker logs <container-name>

# Check if port is in use
sudo netstat -tlnp | grep <port>

# Check disk space (Pis run out fast)
df -h

# Clean up Docker
docker system prune -a
```

### Can’t SSH to Device

```bash
# Use Tailscale IP instead of local IP
ssh pi@100.x.x.x

# If that fails, check Tailscale
tailscale status

# Emergency: physical access + keyboard
# Check if device is on network, restart services
```

### High Latency to LLM

```bash
# Check Jetson load
ssh user@jetson-prime.tailXXXXX.ts.net
nvidia-smi  # GPU usage
htop        # CPU/memory

# Model might be swapping - reduce context length or batch size
```

-----

## Repository Standards

Every repository in the BlackRoad ecosystem should include:

```
repo/
├── .github/
│   └── workflows/
│       └── deploy.yml      # GitHub Actions deployment
├── Dockerfile              # Container definition
├── docker-compose.yml      # Local development
├── .env.example            # Environment variables template
├── README.md               # What this repo does
├── INFRASTRUCTURE.md       # Link to this document
└── src/                    # Actual code
```

### Standard README Section

Every repo README should include:

```markdown
## Infrastructure

This service is part of the BlackRoad OS infrastructure.

- **Runs on**: Pi 5 Alpha / Pi 5 Beta / Jetson (specify)
- **Port**: 8000 (or whatever)
- **Dependencies**: PostgreSQL, Redis, Jetson LLM (list them)
- **Deploy**: Push to main triggers GitHub Actions → Docker → Pi

See [INFRASTRUCTURE.md](./INFRASTRUCTURE.md) for the complete infrastructure guide.
```

-----

## Quick Reference Card

### Tailscale Hostnames

```
pi5-alpha.tailXXXXX.ts.net
pi5-beta.tailXXXXX.ts.net
pi5-gamma.tailXXXXX.ts.net
pi400-delta.tailXXXXX.ts.net
jetson-prime.tailXXXXX.ts.net
droplet-failover.tailXXXXX.ts.net
```

### Common Commands

```bash
# SSH to Pi
ssh pi@pi5-alpha.tailXXXXX.ts.net

# Deploy manually
docker pull ghcr.io/blackroad-os/<service>:latest && docker-compose up -d

# Check tunnel
cloudflared tunnel info

# Check Tailscale
tailscale status

# Restart service
sudo systemctl restart <service>

# View logs
docker logs -f <container>
journalctl -u <service> -f
```

### Port Map

|Port|Service          |
|----|-----------------|
|3000|Frontend / Web UI|
|8000|Main API         |
|8001|Agent Pool API   |
|8080|LLM Inference    |
|5432|PostgreSQL       |
|6379|Redis            |
|9090|Prometheus       |
|3001|Grafana          |

-----

*This document is the single source of truth for BlackRoad OS infrastructure. When in doubt, refer here. When this is wrong, update it.*

**Last updated by**: Claude (Cecilia)  
**Next review date**: January 2026
