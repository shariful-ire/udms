# UDMS — Deployment Guide

## Production Architecture

```
Internet → Nginx (80/443) → FastAPI (8000) + Next.js (3000)
                          → MySQL (3306, internal only)
                          → Redis (6379, internal only)
                          → Celery workers (internal only)
```

---

## Prerequisites

- A Linux server (Ubuntu 22.04 recommended)
- Docker + Docker Compose installed
- Domain name pointing to your server's IP
- Ports 80 and 443 open in firewall

---

## Step 1 — Clone and configure

```bash
git clone <repo-url> /opt/udms
cd /opt/udms
cp backend/.env.example backend/.env
```

Edit `backend/.env` for production:

```env
# SECURITY — generate strong secrets
SECRET_KEY=<openssl rand -hex 32>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# DATABASE
DATABASE_URL=mysql+aiomysql://udms:<strong-password>@mysql:3306/udms_db
MYSQL_ROOT_PASSWORD=<root-password>
MYSQL_PASSWORD=<strong-password>

# REDIS
REDIS_URL=redis://redis:6379/0

# EMAIL (use real SMTP)
SMTP_HOST=smtp.yourprovider.com
SMTP_PORT=587
SMTP_USERNAME=noreply@yourdomain.com
SMTP_PASSWORD=<smtp-password>
EMAILS_FROM_EMAIL=noreply@yourdomain.com

# APP
FRONTEND_URL=https://yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com
ENVIRONMENT=production
DEBUG=false
```

---

## Step 2 — Configure Nginx

Create `/opt/udms/nginx/conf.d/udms.conf`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate     /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # API
    location /api/ {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 10M;
    }

    # Frontend
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Step 3 — Obtain SSL certificate

```bash
# Install certbot
apt install -y certbot

# Obtain certificate (stop Nginx first if running)
certbot certonly --standalone -d yourdomain.com
```

---

## Step 4 — Deploy

```bash
cd /opt/udms

# Build and start production stack
docker compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker compose -f docker-compose.prod.yml exec api alembic upgrade head

# Seed initial provost account only (no test data)
docker compose -f docker-compose.prod.yml exec api python -c "
from app.db.init_db import init_db
import asyncio; asyncio.run(init_db())
"
```

---

## Step 5 — Health check

```bash
curl https://yourdomain.com/api/v1/health
# {"status": "ok", "version": "1.0.0"}
```

---

## Ongoing Operations

### View logs
```bash
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs -f worker
```

### Restart a service
```bash
docker compose -f docker-compose.prod.yml restart api
```

### Database backup
```bash
docker compose -f docker-compose.prod.yml exec mysql \
  mysqldump -u root -p udms_db > backup_$(date +%Y%m%d).sql
```

### Update deployment
```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build api frontend worker beat
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

### SSL renewal
Certbot auto-renews. Add a cron job to reload Nginx after renewal:
```bash
# /etc/cron.d/certbot-reload
0 0 1 * * root certbot renew --quiet && docker compose -f /opt/udms/docker-compose.prod.yml exec nginx nginx -s reload
```

---

## Scaling

The production compose file supports horizontal scaling of the API:

```bash
docker compose -f docker-compose.prod.yml up -d --scale api=3
```

Nginx is configured to load-balance across all API instances.
