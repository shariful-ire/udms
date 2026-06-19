# UDMS — MASTER PROJECT CONTEXT PROMPT

> Paste this entire document into Claude Chat to generate: IEEE Report, Presentation Slides, DBMS Documentation, ER Diagrams, Schema Diagrams, Workflow Diagrams, Viva Questions, and Database Design Analysis.

---

## INSTRUCTION TO CLAUDE

You are given the complete technical context of a full-stack university dining management system called **UDMS**. Using ONLY the information below, generate whatever documentation the user requests — IEEE reports, presentations, ER diagrams (as text/Mermaid), relational schemas, normalization analysis, workflow diagrams, viva Q&A, etc. Do not invent features not described here. All data below was extracted directly from the running codebase.

---

## 1. PROJECT OVERVIEW

**Project Name:** University Dining Management System (UDMS)

**Purpose:** A web-based system to digitize and manage all aspects of a university hall dining operation — meal scheduling, student enrollment, daily menu planning, expense/income tracking, payment verification, financial reporting, and audit logging.

**Target Users:**
- Provost (hall administrator — full system control)
- Dining Manager (manages daily dining operations)
- Customer (enrolled dining student — adds/cancels meals)
- Non-Customer (non-enrolled student — submits one-time meal requests)

**Deployment:** Dockerized multi-container application with 8 services.

**University Context:**
- Departments: IRE, CySE, DSE, EdTE, SE
- Halls: UFTB Boys Hall, UFTB Girls Hall-1, UFTB Girls Hall-2
- Currency: BDT (৳)

---

## 2. TECHNOLOGY STACK

### Backend
- **Language:** Python 3.11
- **Framework:** FastAPI 0.111.0
- **ORM:** SQLAlchemy 2.0.30 (async via aiomysql 0.2.0)
- **ASGI Server:** Uvicorn 0.30.1 (dev), Gunicorn 22.0.0 (prod)
- **Authentication:** JWT (python-jose), Argon2id password hashing, bcrypt fallback
- **Task Queue:** Celery 5.4.0 with Redis broker
- **Email:** FastAPI-Mail 1.4.1 with Jinja2 templates
- **Validation:** Pydantic 2.7.1, pydantic-settings 2.3.0
- **Rate Limiting:** SlowAPI 0.1.9
- **Logging:** Loguru 0.7.2

### Frontend
- **Framework:** Next.js 14.2.4 (React 18.3.1)
- **Language:** JavaScript (JSX), no TypeScript
- **State Management:** Zustand 4.5.4
- **Data Fetching:** TanStack React Query 5.45.1
- **HTTP Client:** Axios 1.7.2
- **UI Components:** Radix UI primitives, Tailwind CSS 3.4.6, Framer Motion
- **Charts:** Recharts 2.12.7
- **Forms:** React Hook Form 7.52.1 + Zod 3.23.8
- **Notifications:** Sonner 1.5.0

### Database
- **DBMS:** MySQL 8.0
- **Connection:** Async via aiomysql, SQLAlchemy AsyncSession
- **Pool:** AsyncAdaptedQueuePool (size=10, max_overflow=20, recycle=3600s)

### Infrastructure (Docker Compose)
| Service | Image/Build | Port |
|---------|------------|------|
| db | mysql:8.0 | 3306 |
| redis | redis:7-alpine | 6379 |
| api | python:3.11-slim (custom) | 8000 |
| worker | same as api (Celery worker) | — |
| beat | same as api (Celery beat) | — |
| flower | same as api (Celery monitor) | 5555 |
| mailhog | mailhog/mailhog | 8025 (UI), 1025 (SMTP) |
| frontend | node:20-alpine (custom) | 3000 |

---

## 3. PROJECT STRUCTURE

```
udms/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── scripts/seed_db.py
│   ├── migrations/versions/001_initial_schema.py
│   └── app/
│       ├── main.py                    # FastAPI app factory + lifespan
│       ├── core/
│       │   ├── config.py              # Pydantic Settings (env-based)
│       │   ├── security.py            # JWT + Argon2 + OTP
│       │   ├── permissions.py         # RBAC roles + permissions
│       │   ├── exceptions.py          # Typed HTTP exceptions
│       │   └── middleware.py          # CORS, security headers, logging
│       ├── db/
│       │   ├── base.py                # SQLAlchemy DeclarativeBase
│       │   ├── session.py             # Async engine + session factory
│       │   └── init_db.py             # Auto-create tables on startup
│       ├── models/
│       │   ├── user.py                # User, RefreshToken
│       │   ├── meal.py                # MealSchedule, DailyMenu, MenuItem, StudentMeal
│       │   └── expense.py             # Expense, Earning, MealRequest, Payment,
│       │                              # MemberPayment, PaymentProof, AuditLog, SystemSetting
│       ├── schemas/                   # Pydantic request/response models
│       ├── repositories/              # Data access layer (async CRUD)
│       ├── services/                  # Business logic layer
│       ├── api/v1/
│       │   ├── router.py              # Central route registry
│       │   ├── deps.py                # Dependency injection (auth, DB, Redis)
│       │   └── endpoints/
│       │       ├── auth.py            # Registration, login, JWT, OTP, password reset
│       │       ├── users.py           # User CRUD, activate/suspend/assign-manager
│       │       ├── dining.py          # Schedules, menus, meals, requests, expenses,
│       │       │                      # earnings, payments, proofs, reports, audit, dashboard
│       │       └── profile.py         # Self-service profile, avatar, password change
│       ├── tasks/                     # Celery async tasks
│       ├── templates/email/           # HTML email templates
│       └── utils/                     # Date, file, formatting helpers
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.mjs
│   └── src/
│       ├── middleware.js              # Route protection (cookie-based)
│       ├── app/
│       │   ├── layout.jsx             # Root layout + font loading
│       │   ├── providers.jsx          # QueryClient, Theme, SessionHydrator
│       │   ├── (auth)/                # Login, register, forgot-password, verify-email
│       │   └── (dashboard)/           # Protected pages
│       │       ├── layout.jsx         # Sidebar + Topbar shell
│       │       ├── dashboard/         # Role-based dashboards
│       │       ├── users/             # User management (Provost)
│       │       ├── dining/            # Schedules, menus, customers
│       │       ├── meals/             # Today's meals, history, summary
│       │       ├── requests/          # Meal request management
│       │       ├── expenses/          # Expense CRUD
│       │       ├── earnings/          # Earning CRUD + edit
│       │       ├── payments/          # Member payment tracking + proof review
│       │       ├── reports/           # Financial reports + export
│       │       ├── audit/             # Audit log viewer
│       │       ├── settings/          # System settings
│       │       └── profile/           # Personal profile
│       ├── components/                # Reusable UI components
│       ├── lib/
│       │   ├── axios.js               # API client + token refresh interceptor
│       │   ├── constants.js           # Roles, statuses, categories, nav links
│       │   ├── queryClient.js         # React Query config + query key factories
│       │   └── utils.js               # formatCurrency, formatDate, cn()
│       └── store/
│           ├── authStore.js           # Zustand auth state
│           └── uiStore.js             # Sidebar collapse state
```

---

## 4. DATABASE DOCUMENTATION

### 4.1 All Tables (14 total)

#### Table: `users`
| Column | Type | Nullable | Key | Notes |
|--------|------|----------|-----|-------|
| id | varchar(36) | NO | PK | UUID v4 |
| student_id | varchar(20) | NO | UNI | e.g. "IRE-2001-001" |
| username | varchar(50) | NO | UNI | lowercase |
| full_name | varchar(150) | NO | | |
| email | varchar(255) | NO | UNI | lowercase |
| password_hash | varchar(255) | NO | | Argon2id |
| role | enum('PROVOST','DINING_MANAGER','CUSTOMER','NON_CUSTOMER') | NO | IDX | |
| department | varchar(100) | YES | | IRE, CySE, DSE, EdTE, SE |
| batch | varchar(20) | YES | | e.g. "2020" |
| hall_name | varchar(100) | YES | | UFTB Boys/Girls Hall |
| phone | varchar(20) | YES | | |
| profile_image | varchar(500) | YES | | avatar path |
| status | enum('ACTIVE','INACTIVE','SUSPENDED') | NO | IDX | default INACTIVE |
| email_verified | tinyint(1) | NO | | default false |
| failed_attempts | int | NO | | for lockout logic |
| locked_until | datetime | YES | | account lockout |
| last_login | datetime | YES | | |
| created_at | datetime | NO | | |
| updated_at | datetime | NO | | auto-update |

#### Table: `refresh_tokens`
| Column | Type | Nullable | Key | Notes |
|--------|------|----------|-----|-------|
| id | varchar(36) | NO | PK | UUID |
| user_id | varchar(36) | NO | FK→users.id | CASCADE delete |
| token_hash | varchar(255) | NO | UNI | SHA-256 of JWT |
| expires_at | datetime | NO | IDX | |
| created_at | datetime | NO | | |

#### Table: `meal_schedules`
| Column | Type | Nullable | Key | Notes |
|--------|------|----------|-----|-------|
| id | varchar(36) | NO | PK | UUID |
| meal_type | enum('BREAKFAST','LUNCH','DINNER') | NO | UNI | one per type |
| start_time | time | NO | | e.g. 07:00 |
| end_time | time | NO | | e.g. 09:00 |
| cancel_deadline | time | NO | | e.g. 06:30 |
| is_active | tinyint(1) | NO | | |
| created_by | varchar(36) | NO | FK→users.id | |
| updated_by | varchar(36) | YES | FK→users.id | |
| created_at, updated_at | datetime | NO | | |

#### Table: `daily_menus`
| Column | Type | Nullable | Key | Notes |
|--------|------|----------|-----|-------|
| id | varchar(36) | NO | PK | UUID |
| date | date | NO | IDX | |
| meal_type | enum('BREAKFAST','LUNCH','DINNER') | NO | | |
| is_cancelled | tinyint(1) | NO | | manager can cancel |
| created_by | varchar(36) | NO | FK→users.id | |
| updated_by | varchar(36) | YES | FK→users.id | |
| created_at, updated_at | datetime | NO | | |
| **Constraint:** UNIQUE(date, meal_type) |

#### Table: `menu_items`
| Column | Type | Nullable | Key | Notes |
|--------|------|----------|-----|-------|
| id | varchar(36) | NO | PK | UUID |
| menu_id | varchar(36) | NO | FK→daily_menus.id | CASCADE |
| food_name | varchar(200) | NO | | |
| quantity | varchar(100) | YES | | e.g. "2 pieces" |
| notes | text | YES | | |
| created_at | datetime | NO | | |

#### Table: `student_meals`
| Column | Type | Nullable | Key | Notes |
|--------|------|----------|-----|-------|
| id | varchar(36) | NO | PK | UUID |
| user_id | varchar(36) | NO | FK→users.id | CASCADE |
| date | date | NO | IDX | |
| meal_type | enum('BREAKFAST','LUNCH','DINNER') | NO | | |
| status | enum('ACTIVE','CANCELLED') | NO | IDX | |
| cancelled_at | datetime | YES | | |
| created_at, updated_at | datetime | NO | | |
| **Constraint:** UNIQUE(user_id, date, meal_type) |

#### Table: `expenses`
| Column | Type | Nullable | Key | Notes |
|--------|------|----------|-----|-------|
| id | varchar(36) | NO | PK | UUID |
| name | varchar(200) | NO | | |
| category | enum('FOOD_PURCHASE','UTILITIES','SALARY','EQUIPMENT','MAINTENANCE','MISCELLANEOUS') | NO | IDX | |
| amount | decimal(12,2) | NO | | |
| description | text | YES | | |
| expense_date | date | NO | IDX | |
| created_by | varchar(36) | NO | FK→users.id | |
| updated_by | varchar(36) | YES | FK→users.id | |
| created_at, updated_at | datetime | NO | | |

#### Table: `earnings`
| Column | Type | Nullable | Key | Notes |
|--------|------|----------|-----|-------|
| id | varchar(36) | NO | PK | UUID |
| description | varchar(200) | NO | | |
| category | enum('MEAL_PAYMENT','DEPOSIT','GRANT','OTHER') | NO | IDX | |
| amount | decimal(12,2) | NO | | |
| earning_date | date | NO | IDX | |
| notes | text | YES | | |
| created_by | varchar(36) | NO | FK→users.id | |
| created_at, updated_at | datetime | NO | | |

#### Table: `meal_requests`
| Column | Type | Nullable | Key | Notes |
|--------|------|----------|-----|-------|
| id | varchar(36) | NO | PK | UUID |
| user_id | varchar(36) | NO | FK→users.id | |
| date | date | NO | IDX | |
| meal_type | enum('BREAKFAST','LUNCH','DINNER') | NO | | |
| reason | text | YES | | |
| status | enum('PENDING_PAYMENT','PENDING_APPROVAL','APPROVED','REJECTED','CANCELLED') | NO | IDX | |
| payment_id | varchar(36) | YES | FK→payments.id | |
| reviewed_by | varchar(36) | YES | FK→users.id | |
| reviewed_at | datetime | YES | | |
| rejection_note | text | YES | | |
| created_at, updated_at | datetime | NO | | |

#### Table: `payments`
| Column | Type | Nullable | Key | Notes |
|--------|------|----------|-----|-------|
| id | varchar(36) | NO | PK | UUID |
| user_id | varchar(36) | NO | FK→users.id | |
| request_id | varchar(36) | YES | | |
| amount | decimal(10,2) | NO | | |
| payment_method | enum('CASH','MOBILE_BANKING','BANK_TRANSFER','OTHER') | NO | | |
| reference_no | varchar(100) | YES | | |
| status | enum('PENDING','COMPLETED','FAILED','REFUNDED') | NO | IDX | |
| note | text | YES | | |
| created_at | datetime | NO | IDX | |
| updated_at | datetime | NO | | |

#### Table: `member_payments`
| Column | Type | Nullable | Key | Notes |
|--------|------|----------|-----|-------|
| id | varchar(36) | NO | PK | UUID |
| user_id | varchar(36) | NO | FK→users.id | CASCADE |
| year | int | NO | | |
| month | int | NO | | 1-12 |
| amount_due | decimal(12,2) | NO | | default 0 |
| amount_paid | decimal(12,2) | NO | | default 0 |
| status | enum('PAID','PENDING') | NO | IDX | manager-controlled |
| created_at, updated_at | datetime | NO | | |
| **Constraint:** UNIQUE(user_id, year, month) |

#### Table: `payment_proofs`
| Column | Type | Nullable | Key | Notes |
|--------|------|----------|-----|-------|
| id | varchar(36) | NO | PK | UUID |
| member_payment_id | varchar(36) | NO | FK→member_payments.id | CASCADE |
| user_id | varchar(36) | NO | FK→users.id | submitter |
| proof_type | enum('IMAGE','TRANSACTION_ID','TEXT_NOTE') | NO | | |
| proof_value | text | NO | | URL, txn ID, or note |
| status | enum('SUBMITTED','APPROVED','REJECTED') | NO | IDX | |
| reviewed_by | varchar(36) | YES | FK→users.id | |
| reviewed_at | datetime | YES | | |
| rejection_note | text | YES | | |
| created_at | datetime | NO | | |

#### Table: `audit_logs`
| Column | Type | Nullable | Key | Notes |
|--------|------|----------|-----|-------|
| id | bigint | NO | PK | auto-increment |
| user_id | varchar(36) | YES | FK→users.id | SET NULL on delete |
| action | varchar(100) | NO | IDX | e.g. "MEAL_ADDED" |
| entity_type | varchar(50) | NO | | e.g. "StudentMeal" |
| entity_id | varchar(36) | YES | | |
| old_value | json | YES | | |
| new_value | json | YES | | |
| ip_address | varchar(45) | YES | | |
| user_agent | varchar(500) | YES | | |
| created_at | datetime | NO | IDX | |

#### Table: `system_settings`
| Column | Type | Nullable | Key | Notes |
|--------|------|----------|-----|-------|
| id | bigint | NO | PK | auto-increment |
| key_name | varchar(100) | NO | UNI | e.g. "meal_price_non_customer" |
| value | text | NO | | |
| description | varchar(500) | YES | | |
| updated_by | varchar(36) | YES | FK→users.id | |
| updated_at | datetime | NO | | |

### 4.2 Foreign Key Relationships (20 total)

| Source Table | Column | → Target Table | Target Column | On Delete |
|-------------|--------|----------------|---------------|-----------|
| refresh_tokens | user_id | users | id | CASCADE |
| meal_schedules | created_by | users | id | — |
| meal_schedules | updated_by | users | id | — |
| daily_menus | created_by | users | id | — |
| daily_menus | updated_by | users | id | — |
| menu_items | menu_id | daily_menus | id | CASCADE |
| student_meals | user_id | users | id | CASCADE |
| expenses | created_by | users | id | — |
| expenses | updated_by | users | id | — |
| earnings | created_by | users | id | — |
| meal_requests | user_id | users | id | — |
| meal_requests | payment_id | payments | id | — |
| meal_requests | reviewed_by | users | id | — |
| payments | user_id | users | id | — |
| member_payments | user_id | users | id | CASCADE |
| payment_proofs | member_payment_id | member_payments | id | CASCADE |
| payment_proofs | user_id | users | id | — |
| payment_proofs | reviewed_by | users | id | — |
| audit_logs | user_id | users | id | SET NULL |
| system_settings | updated_by | users | id | — |

### 4.3 Unique Constraints

| Table | Columns | Name |
|-------|---------|------|
| users | student_id | UNI |
| users | username | UNI |
| users | email | UNI |
| meal_schedules | meal_type | UNI |
| daily_menus | (date, meal_type) | uq_date_meal_type |
| student_meals | (user_id, date, meal_type) | uq_user_date_meal |
| member_payments | (user_id, year, month) | uq_user_year_month |
| refresh_tokens | token_hash | UNI |
| system_settings | key_name | UNI |

---

## 5. DATABASE WORKFLOW

### Data Creation
- **Users**: Created via POST /auth/register (self-registration, starts INACTIVE) or POST /users (admin creation, starts ACTIVE)
- **Meals**: Customer calls POST /meals with {date, meal_type} → creates StudentMeal record with status=ACTIVE
- **Expenses**: Manager calls POST /expenses with {name, category, amount, expense_date}
- **Earnings**: Manager calls POST /earnings with {description, category, amount, earning_date}
- **Menus**: Manager calls POST /dining/menus with {date, meal_type, items[]}
- **Member Payments**: Manager calls POST /member-payments/init → bulk-creates PENDING records for all active customers for a given month
- **Payment Proofs**: Customer calls POST /payment-proofs with {member_payment_id, proof_type, proof_value}

### Data Updates
- **User status**: Provost/Manager toggles ACTIVE↔INACTIVE↔SUSPENDED
- **Meal cancellation**: Customer calls DELETE /meals/{id} → sets status=CANCELLED, cancelled_at=now
- **Payment status**: Manager calls PATCH /member-payments/{id}/mark-paid or mark-pending
- **Proof approval**: Manager calls PATCH /payment-proofs/{id}/approve → also auto-marks payment as PAID

### Data Queries
- **Dashboard**: GET /dashboard/stats → aggregates: total expenses, total earnings, net balance, active customers, 7-day meal session (consumed/remaining/per-meal-cost)
- **Reports**: GET /reports/monthly → calculates meal breakdown (breakfast/lunch/dinner), income, expenses, per-meal cost, net for date range
- **History**: GET /meals/history → paginated student meal records with filters (month, year, type, status)

---

## 6. API DOCUMENTATION (78 endpoints)

### Authentication (9 endpoints)
| Method | Route | Purpose | Auth |
|--------|-------|---------|------|
| POST | /api/v1/auth/register | Self-registration (email+password) | No |
| POST | /api/v1/auth/verify-email | Verify email via OTP | No |
| POST | /api/v1/auth/resend-verification | Resend OTP | No |
| POST | /api/v1/auth/login | Login → returns {access_token, user} + sets refresh cookie | No |
| POST | /api/v1/auth/refresh | Rotate refresh token → new access token | Cookie |
| POST | /api/v1/auth/logout | Invalidate refresh token | Bearer |
| GET | /api/v1/auth/me | Get current user profile | Bearer |
| POST | /api/v1/auth/forgot-password | Request password reset OTP | No |
| POST | /api/v1/auth/reset-password | Reset password with OTP | No |

### User Management (11 endpoints)
| Method | Route | Purpose | Auth |
|--------|-------|---------|------|
| GET | /api/v1/users | List all users (paginated, searchable) | Provost |
| POST | /api/v1/users | Admin-create user | Provost |
| GET | /api/v1/users/stats | Role/status counts | Provost |
| GET | /api/v1/users/recent | Recently joined users | Provost |
| GET | /api/v1/users/{id} | Get user detail | Provost |
| PUT | /api/v1/users/{id} | Update user fields | Provost |
| DELETE | /api/v1/users/{id} | Delete user | Provost |
| PATCH | /api/v1/users/{id}/suspend | Set status=SUSPENDED | Provost/Manager |
| PATCH | /api/v1/users/{id}/activate | Set status=ACTIVE | Provost/Manager |
| PATCH | /api/v1/users/{id}/assign-manager | Set role=DINING_MANAGER | Provost |
| PATCH | /api/v1/users/{id}/remove-manager | Revert to NON_CUSTOMER | Provost |

### Dining Management (11 endpoints)
| Method | Route | Purpose | Auth |
|--------|-------|---------|------|
| GET | /api/v1/dining/schedules | Get all meal schedules | Any |
| PUT | /api/v1/dining/schedules/{type} | Update schedule times | Manager+ |
| GET | /api/v1/dining/menus | Get menus (date range) | Any |
| GET | /api/v1/dining/menus/{date} | Get menus for specific date | Any |
| POST | /api/v1/dining/menus | Create daily menu with items | Manager+ |
| PUT | /api/v1/dining/menus/{id} | Update menu items | Manager+ |
| DELETE | /api/v1/dining/menus/{id} | Delete menu | Manager+ |
| PATCH | /api/v1/dining/menus/{id}/cancel | Cancel menu for a day | Manager+ |
| GET | /api/v1/customers | List enrolled customers | Manager+ |
| POST | /api/v1/customers/{userId} | Enroll user as customer | Manager+ |
| DELETE | /api/v1/customers/{userId} | Remove customer enrollment | Manager+ |

### Meals (5 endpoints)
| Method | Route | Purpose | Auth |
|--------|-------|---------|------|
| GET | /api/v1/meals/today | Today's meal status per type | Customer |
| POST | /api/v1/meals | Add meal enrollment | Customer |
| DELETE | /api/v1/meals/{id} | Cancel meal | Customer |
| GET | /api/v1/meals/history | Paginated meal history | Customer |
| GET | /api/v1/meals/summary | Monthly meal summary | Customer |

### Meal Requests (8 endpoints)
| Method | Route | Purpose | Auth |
|--------|-------|---------|------|
| GET | /api/v1/requests | List requests | Any authenticated |
| POST | /api/v1/requests | Create request | Non-Customer |
| GET | /api/v1/requests/{id} | Get request detail | Owner/Manager |
| DELETE | /api/v1/requests/{id} | Cancel request | Non-Customer |
| POST | /api/v1/requests/payment | Submit bulk payment | Non-Customer |
| POST | /api/v1/requests/{id}/payment | Submit payment for specific request | Non-Customer |
| PATCH | /api/v1/requests/{id}/approve | Approve request → creates meal | Manager+ |
| PATCH | /api/v1/requests/{id}/reject | Reject with note | Manager+ |

### Expenses (5 endpoints)
| Method | Route | Purpose | Auth |
|--------|-------|---------|------|
| GET | /api/v1/expenses | List expenses (paginated, filtered) | Manager+ |
| POST | /api/v1/expenses | Create expense | Manager+ |
| GET | /api/v1/expenses/{id} | Get expense detail | Manager+ |
| PUT | /api/v1/expenses/{id} | Update expense | Manager+ |
| DELETE | /api/v1/expenses/{id} | Delete expense | Manager+ |

### Earnings (5 endpoints)
| Method | Route | Purpose | Auth |
|--------|-------|---------|------|
| GET | /api/v1/earnings | List earnings (paginated, filtered) | Manager+ |
| POST | /api/v1/earnings | Create earning | Manager+ |
| GET | /api/v1/earnings/{id} | Get earning detail | Manager+ |
| PUT | /api/v1/earnings/{id} | Update earning | Manager+ |
| DELETE | /api/v1/earnings/{id} | Delete earning | Manager+ |

### Member Payments (6 endpoints)
| Method | Route | Purpose | Auth |
|--------|-------|---------|------|
| GET | /api/v1/member-payments | List payment records | Any authenticated |
| POST | /api/v1/member-payments/init | Bulk-create month records for active customers | Manager+ |
| GET | /api/v1/member-payments/summary | Paid/pending/proof counts | Manager+ |
| PATCH | /api/v1/member-payments/{id}/mark-paid | Mark as PAID | Manager+ |
| PATCH | /api/v1/member-payments/{id}/mark-pending | Mark as PENDING | Manager+ |
| PATCH | /api/v1/member-payments/{id}/toggle-active | Toggle user ACTIVE↔INACTIVE | Manager+ |

### Payment Proofs (4 endpoints)
| Method | Route | Purpose | Auth |
|--------|-------|---------|------|
| GET | /api/v1/payment-proofs | List proofs (manager=all, member=own) | Any authenticated |
| POST | /api/v1/payment-proofs | Submit proof | Customer |
| PATCH | /api/v1/payment-proofs/{id}/approve | Approve → auto-marks payment PAID | Manager+ |
| PATCH | /api/v1/payment-proofs/{id}/reject | Reject with note | Manager+ |

### Reports (5 endpoints)
| Method | Route | Purpose | Auth |
|--------|-------|---------|------|
| GET | /api/v1/reports/daily | Daily report | Manager+ |
| GET | /api/v1/reports/weekly | Weekly report | Manager+ |
| GET | /api/v1/reports/monthly | Monthly report | Manager+ |
| GET | /api/v1/reports/yearly | Yearly report | Manager+ |
| GET | /api/v1/reports/export | CSV export | Manager+ |

### Dashboard (1 endpoint)
| Method | Route | Purpose | Auth |
|--------|-------|---------|------|
| GET | /api/v1/dashboard/stats | Aggregated stats: totals, net balance, meal session | Any authenticated |

### Audit (3 endpoints), Profile (4 endpoints), Settings (2 endpoints)
Standard CRUD for audit log viewing (Provost only), self-service profile management, and system settings.

**Standard API Response Format:**
```json
{ "success": true, "data": {...}, "meta": { "page": 1, "per_page": 20, "total": 100, "total_pages": 5, "has_next": true, "has_prev": false } }
```

---

## 7. BUSINESS LOGIC DOCUMENTATION

### 7.1 Authentication Flow
1. User registers → password hashed with Argon2id → OTP sent via email → status=INACTIVE
2. User verifies email with OTP → status=ACTIVE
3. Login: verify credentials → issue JWT access token (15min) + HttpOnly refresh token cookie (7 days)
4. Token refresh: validate refresh token hash in DB → issue new pair → old token invalidated
5. Account lockout: 5 failed attempts → locked for 15 minutes
6. Password reset: OTP via email → verify OTP → set new password

### 7.2 Meal Management Flow
1. Manager creates MealSchedule (BREAKFAST/LUNCH/DINNER with time windows)
2. Manager creates DailyMenu for each date+type with food items
3. Customer adds meal (POST /meals) if: schedule is active, menu not cancelled, before start_time, no duplicate
4. Customer cancels meal if: before cancel_deadline
5. 7-day session calculates: total_possible = active_customers × 3 × 7; consumed = actual ACTIVE meals; remaining = possible - consumed; per_meal_cost = session_expenses / consumed

### 7.3 Non-Customer Meal Request Flow
1. Non-Customer submits request → status=PENDING_PAYMENT
2. Non-Customer submits payment (amount, method, reference) → status=PENDING_APPROVAL
3. Manager approves → status=APPROVED, StudentMeal record created
4. Manager rejects → status=REJECTED with note

### 7.4 Expense/Earning Management
- Manager creates/edits/deletes expenses with category and date
- Manager creates/edits/deletes earnings with category and date
- Net balance = total_earnings - total_expenses (computed live)
- Reports aggregate by period with category breakdowns

### 7.5 Payment Verification Flow
1. Manager initializes month → creates PENDING records for all active customers
2. Customer submits proof (TRANSACTION_ID, IMAGE URL, or TEXT_NOTE)
3. Manager reviews: Approve → auto-sets payment to PAID; Reject → adds rejection note
4. Manager can also directly mark PAID/PENDING without proof

### 7.6 User Status & Permissions
- ACTIVE: full access to role-based features
- INACTIVE: cannot log in, excluded from meal calculations
- SUSPENDED: cannot log in
- Only ACTIVE CUSTOMER users count in meal session totals
- Manager can toggle active/inactive; Provost can do everything

### 7.7 Role-Based Access Control (RBAC)
| Permission | Provost | Manager | Customer | Non-Customer |
|-----------|---------|---------|----------|-------------|
| Manage Users | ✓ | | | |
| Manage Expenses | ✓ | ✓ | | |
| Manage Earnings | ✓ | ✓ | | |
| Manage Payments | ✓ | ✓ | | |
| Toggle User Status | ✓ | ✓ | | |
| Manage Menus | ✓ | ✓ | | |
| Approve Requests | ✓ | ✓ | | |
| View Reports | ✓ | ✓ | | |
| Add/Cancel Meals | | | ✓ | |
| Submit Proof | | | ✓ | |
| Submit Request | | | | ✓ |
| View Audit Logs | ✓ | | | |

---

## 8. DBMS ANALYSIS

### 8.1 Entity-Relationship Summary

**Entities:** User, RefreshToken, MealSchedule, DailyMenu, MenuItem, StudentMeal, Expense, Earning, MealRequest, Payment, MemberPayment, PaymentProof, AuditLog, SystemSetting

**Key Relationships:**
- User 1:N RefreshToken (one user has many sessions)
- User 1:N StudentMeal (one customer has many meal records)
- User 1:N MemberPayment (one customer has one payment record per month)
- User 1:N MealRequest (one non-customer has many requests)
- User 1:N Expense (created_by)
- User 1:N Earning (created_by)
- DailyMenu 1:N MenuItem (one menu has many food items)
- MealRequest N:1 Payment (one request links to one payment)
- MemberPayment 1:N PaymentProof (one payment can have multiple proof submissions)
- User 1:N AuditLog (one user generates many audit entries)

### 8.2 Cardinality
- users ↔ student_meals: 1:M
- users ↔ member_payments: 1:M (unique per user+year+month)
- users ↔ meal_requests: 1:M
- daily_menus ↔ menu_items: 1:M
- member_payments ↔ payment_proofs: 1:M
- meal_requests ↔ payments: M:1

### 8.3 Normalization Analysis
- **1NF:** All tables have atomic values, no repeating groups, all have primary keys
- **2NF:** No partial dependencies (all non-key attributes depend on the full PK; composite keys use separate junction constraints)
- **3NF:** No transitive dependencies (e.g., user department/hall stored directly on user, not through a separate department table — acceptable denormalization for a small fixed set)
- **Potential 3NF violation:** department and hall_name on users could be normalized into separate tables, but with only 5 departments and 3 halls, denormalization is pragmatic

### 8.4 Referential Integrity
- CASCADE deletes on: refresh_tokens, student_meals, member_payments, payment_proofs, menu_items
- SET NULL on: audit_logs.user_id (preserves log when user deleted)
- RESTRICT (default) on: expenses, earnings, meal_requests (prevent orphan data)

### 8.5 Indexes
- All primary keys indexed automatically
- All foreign keys indexed (MySQL creates implicit indexes)
- Additional indexes: users(student_id, username, email, role, status), expenses(category, expense_date), earnings(category, earning_date), student_meals(date, status), audit_logs(action, created_at), member_payments(status)

---

## 9. DOCUMENTATION SOURCE MAP

### Backend — Models & Database
- `backend/app/models/user.py` — User, RefreshToken models
- `backend/app/models/meal.py` — MealSchedule, DailyMenu, MenuItem, StudentMeal models
- `backend/app/models/expense.py` — Expense, Earning, MealRequest, Payment, MemberPayment, PaymentProof, AuditLog, SystemSetting models
- `backend/app/db/base.py` — SQLAlchemy DeclarativeBase
- `backend/app/db/session.py` — Async engine + session factory
- `backend/app/db/init_db.py` — Auto table creation + seeding

### Backend — API Layer
- `backend/app/api/v1/router.py` — Central route registry (14 routers)
- `backend/app/api/v1/deps.py` — Auth dependencies, Redis client, DB session
- `backend/app/api/v1/endpoints/auth.py` — Authentication endpoints
- `backend/app/api/v1/endpoints/users.py` — User management endpoints
- `backend/app/api/v1/endpoints/dining.py` — All dining-related endpoints (schedules, menus, meals, requests, expenses, earnings, payments, proofs, reports, audit, dashboard)
- `backend/app/api/v1/endpoints/profile.py` — Profile + settings endpoints

### Backend — Business Logic
- `backend/app/services/auth_service.py` — Registration, login, OTP, password reset
- `backend/app/services/dining_service.py` — Menu CRUD, customer management
- `backend/app/services/meal_service.py` — MealService, MealRequestService, ExpenseService, EarningService, MemberPaymentService, DashboardService, ReportService
- `backend/app/services/email_service.py` — Email sending via FastAPI-Mail

### Backend — Data Access
- `backend/app/repositories/base.py` — Generic async CRUD repository
- `backend/app/repositories/user_repo.py` — UserRepository, RefreshTokenRepository
- `backend/app/repositories/meal_repo.py` — All dining repositories (MealSchedule, DailyMenu, StudentMeal, MealRequest, Payment, Expense, Earning, MemberPayment, PaymentProof, Audit)

### Backend — Core
- `backend/app/core/config.py` — Settings (pydantic-settings, env-based)
- `backend/app/core/security.py` — JWT creation/verification, Argon2id hashing, OTP generation
- `backend/app/core/permissions.py` — RBAC: 4 roles, 21 permissions, role-permission mapping
- `backend/app/core/exceptions.py` — 20+ typed HTTP exceptions
- `backend/app/core/middleware.py` — CORS, security headers, request logging, timing
- `backend/app/main.py` — FastAPI app factory, lifespan events

### Backend — Configuration
- `backend/requirements.txt` — Python dependencies
- `backend/Dockerfile` — Multi-stage (builder + runtime)
- `backend/.env` — Environment variables
- `backend/scripts/seed_db.py` — Database seeder (test data)

### Frontend — Pages
- `frontend/src/app/(dashboard)/dashboard/page.jsx` — Role-based dashboards (Manager/Customer/NonCustomer)
- `frontend/src/app/(dashboard)/expenses/page.jsx` — Expense list + CRUD
- `frontend/src/app/(dashboard)/earnings/page.jsx` — Earning list + CRUD
- `frontend/src/app/(dashboard)/earnings/[id]/page.jsx` — Earning edit
- `frontend/src/app/(dashboard)/payments/page.jsx` — Member payment tracking + proof review
- `frontend/src/app/(dashboard)/users/page.jsx` — User management
- `frontend/src/app/(dashboard)/meals/page.jsx` — Today's meals
- `frontend/src/app/(auth)/login/page.jsx` — Login page

### Frontend — Core
- `frontend/src/lib/axios.js` — API client with JWT refresh interceptor
- `frontend/src/lib/constants.js` — Roles, statuses, categories, nav config
- `frontend/src/lib/queryClient.js` — React Query config + query keys
- `frontend/src/lib/utils.js` — Formatting utilities
- `frontend/src/store/authStore.js` — Zustand auth state
- `frontend/src/middleware.js` — Route protection middleware
- `frontend/src/app/providers.jsx` — Session hydration + providers

### Configuration
- `docker-compose.yml` — 8-service Docker setup
- `frontend/Dockerfile` — Multi-stage Next.js build
- `frontend/package.json` — Frontend dependencies
- `frontend/next.config.mjs` — Next.js configuration (rewrites, images, headers)

---

## END OF MASTER CONTEXT

Use all information above to generate any documentation the user requests. Every fact comes from the actual running codebase — do not add features or tables not listed here.
