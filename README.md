<div align="center">

# 🍽️ University Dining Management System

**A full-stack platform for managing university dining hall operations at scale.**

Meal scheduling · Customer enrollment · Expense tracking · Financial reporting · Role-based access control

<br/>

![Next.js](https://img.shields.io/badge/Next.js_14-000000?style=for-the-badge&logo=next.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL_8-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

</div>

---

## ✦ Tech Stack

| Layer | Technologies |
|:---|:---|
| **Frontend** | Next.js 14 (App Router) · Tailwind CSS · ShadCN UI · Zustand · TanStack Query |
| **Backend** | FastAPI · SQLAlchemy (async) · Alembic · Celery · Redis |
| **Database** | MySQL 8 |
| **Auth** | JWT access tokens (in-memory) + Refresh tokens (HttpOnly cookie) · Argon2id |
| **Email** | SMTP via Celery tasks · Jinja2 templates · MailHog (dev) |
| **Deployment** | Docker Compose · Nginx reverse proxy · Certbot SSL |

---

## ✦ Roles

| Role | Access |
|:---|:---|
| `PROVOST` | System administrator. Full access to all features. Inherits dining manager permissions when no manager is assigned. |
| `DINING_MANAGER` | Manages schedules, menus, customers, expenses, and reviews enrollment requests. |
| `CUSTOMER` | Enrolled student. Can add or cancel meals and view meal history. |
| `NON_CUSTOMER` | Registered student. Can submit enrollment requests. |

---

## ✦ Quick Start

> **Prerequisites:** Docker Desktop ≥ 24 · Node.js ≥ 20 *(frontend only)* · Python 3.11+ *(backend only)*

### Step 1 — Clone and configure

```bash
git clone <repo-url>
cd udms
cp backend/.env.example backend/.env
# Edit backend/.env with your settings
```

### Step 2 — Start all services

```bash
docker compose up -d
```

| Service | Port | URL |
|:---|:---:|:---|
| Next.js | `3000` | http://localhost:3000 |
| FastAPI | `8000` | http://localhost:8000/docs |
| Flower (tasks) | `5555` | http://localhost:5555 |
| MailHog (email) | `8025` | http://localhost:8025 |
| MySQL | `3306` | — |
| Redis | `6379` | — |

### Step 3 — Seed the database

```bash
docker compose exec api python scripts/seed_db.py
```

### Step 4 — Open the app

| | URL |
|:---|:---|
| 🌐 Application | http://localhost:3000 |
| 📖 API Reference | http://localhost:8000/docs |
| 📬 Email Inbox | http://localhost:8025 |
| 📊 Task Monitor | http://localhost:5555 |

---

## ✦ Seed Accounts

> Full credential list in [`docs/SEED_ACCOUNTS.md`](docs/SEED_ACCOUNTS.md)

| Role | Username | Password |
|:---|:---|:---|
| `PROVOST` | `provost` | `Admin@1234!` |
| `DINING_MANAGER` | `diningmgr` | `Manager@1234!` |
| `CUSTOMER` | `student_customer` | `Student@1234!` |
| `NON_CUSTOMER` | `student_normal` | `Student@1234!` |

---

## ✦ Project Structure

```
udms/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # FastAPI route handlers
│   │   ├── core/               # Config, security, permissions, middleware
│   │   ├── db/                 # Session, models, init
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── repositories/       # Database access layer
│   │   ├── schemas/            # Pydantic request/response models
│   │   ├── services/           # Business logic
│   │   ├── tasks/              # Celery async tasks
│   │   ├── templates/email/    # Jinja2 email templates
│   │   └── utils/              # Helpers
│   ├── migrations/             # Alembic migrations
│   ├── scripts/                # Seed script
│   ├── tests/                  # Pytest unit + integration tests
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                # Next.js App Router pages
│   │   ├── components/         # Reusable UI components
│   │   ├── lib/                # Axios, utils, hooks, constants
│   │   └── store/              # Zustand state stores
│   └── Dockerfile
├── docker-compose.yml          # Development stack
├── docker-compose.prod.yml     # Production stack with Nginx + SSL
└── docs/
    ├── INSTALLATION.md
    ├── DEPLOYMENT.md
    ├── API.md
    └── SEED_ACCOUNTS.md
```

---

## ✦ Documentation

| | Guide | Description |
|:---:|:---|:---|
| 📥 | [Installation Guide](docs/INSTALLATION.md) | Set up the project locally from scratch |
| 🚀 | [Deployment Guide](docs/DEPLOYMENT.md) | Deploy to production with Nginx + SSL |
| ⚙️ | [API Reference](docs/API.md) | Full endpoint documentation |
| 👥 | [Seed Accounts](docs/SEED_ACCOUNTS.md) | Test credentials for all roles |

---

## ✦ Running Tests

**Backend**

```bash
cd backend
pip install -r requirements-dev.txt
pytest -v
```

**Frontend**

```bash
cd frontend
npm run type-check
npm run lint
```


---
diningmgr / Manager@1234!
or provost / Admin@1234!
---