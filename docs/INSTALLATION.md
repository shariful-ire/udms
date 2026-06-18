# UDMS — Installation Guide

## Prerequisites

| Tool | Minimum Version |
|---|---|
| Docker | 24.x |
| Docker Compose | 2.x (included with Docker Desktop) |
| Node.js | 20.x (optional, for local frontend dev) |
| Python | 3.11+ (optional, for local backend dev) |

---

## Docker Installation (Recommended)

### 1. Configure environment

```bash
cd udms
cp backend/.env.example backend/.env
```

Open `backend/.env` and set at minimum:

```env
SECRET_KEY=<generate with: openssl rand -hex 32>
DATABASE_URL=mysql+aiomysql://udms:udmspass@mysql:3306/udms_db
REDIS_URL=redis://redis:6379/0
SMTP_HOST=mailhog        # Use real SMTP in production
SMTP_PORT=1025
```

### 2. Start all services

```bash
docker compose up -d
```

Wait ~30 seconds for MySQL to initialise, then:

```bash
# Run migrations
docker compose exec api alembic upgrade head

# Seed test data
docker compose exec api python scripts/seed_db.py
```

### 3. Verify

```bash
docker compose ps       # All services should show "Up"
curl http://localhost:8000/health   # {"status": "ok"}
```

Open http://localhost:3000 in your browser.

---

## Local Development (Without Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configure environment
cp .env.example .env
# Edit .env: point DATABASE_URL to a local MySQL instance

# Run migrations
alembic upgrade head

# Seed database
python scripts/seed_db.py

# Start API server
uvicorn app.main:app --reload --port 8000
```

You also need Redis and MySQL running locally (or use Docker for those services):

```bash
# Start just the infrastructure services
docker compose up -d mysql redis mailhog
```

### Frontend

```bash
cd frontend

npm install

# Configure
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start dev server
npm run dev
```

Open http://localhost:3000.

---

## Running Tests

```bash
cd backend

# Unit + integration tests (uses SQLite in-memory — no MySQL needed)
pytest -v

# With coverage
pytest --cov=app --cov-report=term-missing
```

---

## Common Issues

### MySQL won't start
```bash
docker compose logs mysql
# If "table already exists" errors: remove the volume
docker compose down -v && docker compose up -d
```

### Port conflicts
Edit the `ports` mapping in `docker-compose.yml`. Default ports:
- 3000 (frontend), 8000 (API), 3306 (MySQL), 6379 (Redis), 8025 (MailHog), 5555 (Flower)

### Email not arriving
MailHog catches all outgoing email in development. View captured emails at http://localhost:8025.
