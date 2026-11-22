# AICTE NEXUS — Production Deployment Guide

## 1. Prerequisites

- Linux Server (Ubuntu 22.04 LTS / Debian 12 / RHEL 9) or Windows Server 2022
- PostgreSQL 13+ with `pg_trgm`, `fuzzystrmatch`, and `uuid-ossp` extensions enabled
- Redis 7+ or 8+
- Python 3.12+ or 3.13+
- Node.js 20+ or 22+ (LTS)

---

## 2. Docker Compose Deployment

The repository includes standard container definitions for single-command production deployment:

```bash
docker compose up -d --build
```

### `docker-compose.yml` Structure:
```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: aicte_nexus
      POSTGRES_USER: aicte_admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    environment:
      - DATABASE_URL=postgresql+asyncpg://aicte_admin:${DB_PASSWORD}@db:5432/aicte_nexus
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    environment:
      - NEXT_PUBLIC_API_URL=/api/v1
    depends_on:
      - backend
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

---

## 3. Reverse Proxy & SSL Configuration (Nginx)

```nginx
server {
    listen 80;
    server_name nexus.aicte-india.org;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name nexus.aicte-india.org;

    ssl_certificate /etc/letsencrypt/live/nexus.aicte-india.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/nexus.aicte-india.org/privkey.pem;

    # Frontend Next.js
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend FastAPI
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

