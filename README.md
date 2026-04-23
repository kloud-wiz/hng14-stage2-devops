# HNG14 Stage 2 — Containerized Microservices with CI/CD

A production-ready job processing system built with Docker, Docker Compose, and a full GitHub Actions CI/CD pipeline.

## Architecture

The application consists of four services:

- **Frontend** (Node.js/Express) — UI for submitting and tracking jobs
- **API** (Python/FastAPI) — creates jobs and serves status updates
- **Worker** (Python) — picks up and processes jobs from the queue
- **Redis** — shared message queue between API and worker

All services communicate over an internal Docker network. Redis is never exposed to the host.

## Prerequisites

- Git
- Docker Engine v24+
- Docker Compose plugin v2.20+

## Quickstart — Run on a Clean Machine

### 1. Clone the repository

```bash
git clone https://github.com/kloud-wiz/hng14-stage2-devops.git
cd hng14-stage2-devops
```

### 2. Create your environment file

```bash
cp .env.example .env
```

Open `.env` and set a strong Redis password:

```bash
nano .env
```

Required variables:

```
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_strong_password_here
API_URL=http://api:8000
API_PORT=8000
FRONTEND_PORT=3500
APP_ENV=production
```

### 3. Build and start the stack

```bash
docker compose up --build -d
```

### 4. Verify all services are healthy

```bash
docker compose ps
```

Expected output — all services should show `(healthy)`:

```
NAME                             SERVICE    STATUS
hng14-stage2-devops-api-1        api        Up (healthy)
hng14-stage2-devops-frontend-1   frontend   Up (healthy)
hng14-stage2-devops-redis-1      redis      Up (healthy)
hng14-stage2-devops-worker-1     worker     Up (healthy)
```

### 5. Access the application

Open your browser and navigate to:

```
http://localhost:3500
```

Click **Submit New Job** — you should see the job appear and transition from `queued` to `completed` within a few seconds.

## Stopping the Stack

```bash
docker compose down
```

To also remove volumes (clears Redis data):

```bash
docker compose down -v
```

## Running Tests

Install dependencies:

```bash
pip install -r api/requirements.txt
```

Run tests with coverage:

```bash
pytest api/tests/ -v --cov=api --cov-report=term-missing
```

## CI/CD Pipeline

The GitHub Actions pipeline runs on every push and pull request to `main` with the following stages in strict order:

| Stage | Description |
|---|---|
| Lint | flake8 (Python), eslint (JS), hadolint (Dockerfiles) |
| Test | pytest with Redis mocked, coverage report uploaded as artifact |
| Build | Build all images, tag with git SHA + latest, push to local registry |
| Security Scan | Trivy scans all images, fails on CRITICAL CVEs, SARIF uploaded as artifact |
| Integration Test | Full stack brought up, job submitted, polled to completion, asserted, torn down |
| Deploy | SSH rolling update to production server — only on pushes to main |

A failure in any stage stops all subsequent stages.

## Required GitHub Secrets for Deploy

| Secret | Description |
|---|---|
| `DEPLOY_HOST` | Production server IP or hostname |
| `DEPLOY_USER` | SSH username |
| `DEPLOY_SSH_KEY` | Private SSH key for authentication |

## Project Structure

```
.
├── api/                  # FastAPI application
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── tests/
│       └── test_main.py
├── worker/               # Job processing worker
│   ├── Dockerfile
│   ├── worker.py
│   └── requirements.txt
├── frontend/             # Node.js/Express UI
│   ├── Dockerfile
│   ├── app.js
│   └── views/
│       └── index.html
├── docker-compose.yml
├── .env.example
├── FIXES.md
└── .github/
    └── workflows/
        └── pipeline.yml
```

## Bugs Fixed

See [FIXES.md](./FIXES.md) for a full list of all 23 bugs found and fixed in the starter repository.

