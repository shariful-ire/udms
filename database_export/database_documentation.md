# UDMS — Complete Database Documentation

## 1. Overview

The University Dining Management System (UDMS) database consists of **14 tables** built on **MySQL 8.0** with the **InnoDB** storage engine. It manages the complete lifecycle of a university hall dining operation — user accounts, meal scheduling, enrollment tracking, financial records, payment verification, and audit logging.

**Key statistics:**
- 14 tables
- 20 foreign key constraints
- 9 unique constraints
- 30+ indexes
- 8 ENUM types
- UUID-based primary keys (except `audit_logs` and `system_settings` which use auto-increment)

---

## 2. Schema Design Principles

### 2.1 Primary Key Strategy
- **UUID v4** (`VARCHAR(36)`) for all entity tables — avoids auto-increment collisions in distributed environments and prevents ID enumeration attacks.
- **BIGINT AUTO_INCREMENT** for `audit_logs` and `system_settings` — high-volume append-only tables where sequential IDs are optimal.

### 2.2 Character Set
- All tables use `utf8mb4` charset with `utf8mb4_unicode_ci` collation to support full Unicode (including Bengali script used in the university context).

### 2.3 Timestamp Conventions
- `created_at`: Set once via `DEFAULT CURRENT_TIMESTAMP`, never updated.
- `updated_at`: Auto-maintained via `ON UPDATE CURRENT_TIMESTAMP`.
- All timestamps stored in server timezone (UTC recommended).

### 2.4 Soft Deletes vs Hard Deletes
- **Student meals**: Soft delete via `status = 'CANCELLED'` + `cancelled_at` timestamp.
- **Meal requests**: Status-based lifecycle (`CANCELLED` is a terminal state).
- **Payments**: Never deleted; status transitions track lifecycle.
- **Users**: Hard delete cascades to sessions, meals, and billing records.
- **Audit logs**: Never deleted (immutable).

---

## 3. Table Groups

### Group A: Identity & Authentication
| Table | Rows (typical) | Purpose |
|-------|----------------|---------|
| `users` | 50–500 | All system accounts |
| `refresh_tokens` | 10–100 | Active JWT sessions |

### Group B: Meal Operations
| Table | Rows (typical) | Purpose |
|-------|----------------|---------|
| `meal_schedules` | 3 (fixed) | Time windows for BREAKFAST/LUNCH/DINNER |
| `daily_menus` | 90+ (grows daily) | Menu definitions per date + meal |
| `menu_items` | 300+ | Food items within menus |
| `student_meals` | 10,000+ | Individual meal enrollments |

### Group C: Financial Records
| Table | Rows (typical) | Purpose |
|-------|----------------|---------|
| `expenses` | 100+ | Operational costs |
| `earnings` | 50+ | Income records |
| `payments` | 50+ | Non-customer payment transactions |
| `member_payments` | 500+ | Monthly billing per customer |
| `payment_proofs` | 200+ | Payment evidence |

### Group D: Non-Customer Workflow
| Table | Rows (typical) | Purpose |
|-------|----------------|---------|
| `meal_requests` | 100+ | One-time meal requests with approval flow |
| `payments` | (shared) | Linked payments for requests |

### Group E: System
| Table | Rows (typical) | Purpose |
|-------|----------------|---------|
| `audit_logs` | 10,000+ | Immutable activity log |
| `system_settings` | 8 (fixed) | Runtime configuration |

---

## 4. ENUM Definitions

| ENUM Name | Values | Used In |
|-----------|--------|---------|
| User Role | `PROVOST`, `DINING_MANAGER`, `CUSTOMER`, `NON_CUSTOMER` | `users.role` |
| User Status | `ACTIVE`, `INACTIVE`, `SUSPENDED` | `users.status` |
| Meal Type | `BREAKFAST`, `LUNCH`, `DINNER` | `meal_schedules`, `daily_menus`, `student_meals`, `meal_requests` |
| Student Meal Status | `ACTIVE`, `CANCELLED` | `student_meals.status` |
| Request Status | `PENDING_PAYMENT`, `PENDING_APPROVAL`, `APPROVED`, `REJECTED`, `CANCELLED` | `meal_requests.status` |
| Payment Method | `CASH`, `MOBILE_BANKING`, `BANK_TRANSFER`, `OTHER` | `payments.payment_method` |
| Payment Status | `PENDING`, `COMPLETED`, `FAILED`, `REFUNDED` | `payments.status` |
| Expense Category | `FOOD_PURCHASE`, `UTILITIES`, `SALARY`, `EQUIPMENT`, `MAINTENANCE`, `MISCELLANEOUS` | `expenses.category` |
| Earning Category | `MEAL_PAYMENT`, `DEPOSIT`, `GRANT`, `OTHER` | `earnings.category` |
| Member Payment Status | `PAID`, `PENDING` | `member_payments.status` |
| Proof Type | `IMAGE`, `TRANSACTION_ID`, `TEXT_NOTE` | `payment_proofs.proof_type` |
| Proof Status | `SUBMITTED`, `APPROVED`, `REJECTED` | `payment_proofs.status` |

---

## 5. Normalization Analysis

### First Normal Form (1NF) — Satisfied
- All columns contain atomic values (no arrays, no comma-separated lists).
- No repeating groups — menu items are in a separate `menu_items` table, not stored as a JSON array.
- Every table has a defined primary key.

### Second Normal Form (2NF) — Satisfied
- No partial dependencies. All non-key attributes depend on the full primary key.
- Composite unique constraints (`daily_menus(date, meal_type)`, `student_meals(user_id, date, meal_type)`, `member_payments(user_id, year, month)`) use surrogate UUID primary keys, so non-key columns depend only on the PK.

### Third Normal Form (3NF) — Satisfied with Pragmatic Exceptions
- No transitive dependencies in the general case.
- **Deliberate denormalization:** `department` and `hall_name` are stored directly on `users` rather than as FK references to separate lookup tables. This is acceptable because:
  - Only 5 departments (`IRE`, `CySE`, `DSE`, `EdTE`, `SE`) — a fixed, small set.
  - Only 3 halls (`UFTB Boys Hall`, `UFTB Girls Hall-1`, `UFTB Girls Hall-2`) — a fixed, small set.
  - The values never change independently of the user record.
  - Normalizing them would add join overhead with no practical benefit.

### BCNF — Satisfied
- In every table, the determinant of every functional dependency is a superkey.

---

## 6. Indexing Strategy

### Primary Key Indexes (automatic)
Every table's PK is automatically indexed by InnoDB.

### Foreign Key Indexes
All FK columns have explicit indexes for efficient JOIN performance.

### Functional Indexes

| Table | Index | Columns | Purpose |
|-------|-------|---------|---------|
| `users` | `idx_users_student_id` | `student_id` | Student ID lookup |
| `users` | `idx_users_username` | `username` | Login lookup |
| `users` | `idx_users_email` | `email` | Email verification lookup |
| `users` | `idx_users_role` | `role` | Filter by role (dashboard queries) |
| `users` | `idx_users_status` | `status` | Filter active users (meal calculations) |
| `refresh_tokens` | `idx_rt_expires` | `expires_at` | Expired token cleanup |
| `meal_schedules` | `idx_ms_active` | `is_active` | Active schedule lookup |
| `daily_menus` | `idx_dm_date` | `date` | Date-range menu queries |
| `student_meals` | `idx_sm_date` | `date` | Daily meal counts |
| `student_meals` | `idx_sm_status` | `status` | Active vs cancelled filtering |
| `expenses` | `idx_exp_category` | `category` | Category-based reports |
| `expenses` | `idx_exp_date` | `expense_date` | Date-range financial queries |
| `earnings` | `idx_earn_category` | `category` | Category-based reports |
| `earnings` | `idx_earn_date` | `earning_date` | Date-range financial queries |
| `meal_requests` | `idx_mr_status` | `status` | Pending request queue |
| `meal_requests` | `idx_mr_date` | `date` | Date filtering |
| `payments` | `idx_pay_status` | `status` | Pending payment lookup |
| `payments` | `idx_pay_created` | `created_at` | Recent payment queries |
| `member_payments` | `idx_mp_status` | `status` | Paid vs pending filtering |
| `payment_proofs` | `idx_pp_status` | `status` | Pending review queue |
| `audit_logs` | `idx_al_action` | `action` | Filter by action type |
| `audit_logs` | `idx_al_entity` | `entity_type, entity_id` | Entity history lookup |
| `audit_logs` | `idx_al_created` | `created_at` | Time-range log queries |

---

## 7. Referential Integrity Rules

### CASCADE Deletes
When a parent record is deleted, all child records are automatically deleted:
- Deleting a **user** cascades to: `refresh_tokens`, `student_meals`, `member_payments`
- Deleting a **daily_menu** cascades to: `menu_items`
- Deleting a **member_payment** cascades to: `payment_proofs`

### SET NULL
- Deleting a **user** sets `audit_logs.user_id` to NULL (preserves the log).

### RESTRICT (default)
- Cannot delete a user who has created expenses, earnings, meal requests, or payments.
- Must reassign or delete those records first.

---

## 8. Data Flow Diagrams

### 8.1 Customer Meal Lifecycle
```
Customer adds meal → student_meals (ACTIVE)
Customer cancels   → student_meals (CANCELLED, cancelled_at set)
Dashboard counts   → SELECT COUNT WHERE status='ACTIVE'
Monthly report     → GROUP BY meal_type + date range
```

### 8.2 Non-Customer Meal Request Pipeline
```
Non-customer → meal_requests (PENDING_PAYMENT)
              → payments (PENDING)
              → meal_requests (PENDING_APPROVAL) + payments (COMPLETED)
Manager      → meal_requests (APPROVED) + student_meals (ACTIVE)
           or → meal_requests (REJECTED, rejection_note set)
```

### 8.3 Monthly Billing Pipeline
```
Manager initializes → member_payments (PENDING, amount_due set)
Customer submits    → payment_proofs (SUBMITTED)
Manager approves    → payment_proofs (APPROVED) + member_payments (PAID)
Manager rejects     → payment_proofs (REJECTED, rejection_note set)
```

### 8.4 Financial Reporting
```
expenses + earnings → SUM/GROUP BY category/date → Dashboard stats
student_meals (ACTIVE count) + expenses → per_meal_cost calculation
member_payments (PAID vs PENDING) → collection tracking
```

---

## 9. Role-Based Access Control (RBAC)

The `users.role` ENUM drives all authorization decisions:

| Permission | PROVOST | DINING_MANAGER | CUSTOMER | NON_CUSTOMER |
|-----------|---------|----------------|----------|--------------|
| Manage Users | Yes | — | — | — |
| View Audit Logs | Yes | — | — | — |
| Manage Expenses | Yes | Yes | — | — |
| Manage Earnings | Yes | Yes | — | — |
| Manage Menus | Yes | Yes | — | — |
| Approve Requests | Yes | Yes | — | — |
| View Reports | Yes | Yes | — | — |
| Manage Payments | Yes | Yes | — | — |
| Toggle User Status | Yes | Yes | — | — |
| Add/Cancel Meals | — | — | Yes | — |
| Submit Payment Proof | — | — | Yes | — |
| Submit Meal Request | — | — | — | Yes |
| View Menu & Schedules | Yes | Yes | Yes | Yes |
| Manage Own Profile | Yes | Yes | Yes | Yes |

---

## 10. Source Code References

| Component | File Path |
|-----------|-----------|
| User model | `backend/app/models/user.py` |
| Meal models | `backend/app/models/meal.py` |
| Financial models | `backend/app/models/expense.py` |
| Base class | `backend/app/db/base.py` |
| Session factory | `backend/app/db/session.py` |
| DB initialization | `backend/app/db/init_db.py` |
| Migration | `backend/migrations/versions/001_initial_schema.py` |
| Seed script | `backend/scripts/seed_db.py` |
| Permissions | `backend/app/core/permissions.py` |
| DB config | `backend/app/core/config.py` |
