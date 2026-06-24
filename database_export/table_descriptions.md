# UDMS — Table Descriptions

> 14 tables extracted from SQLAlchemy models in `backend/app/models/`

---

## 1. `users`

**Purpose:** Central identity table for all system accounts — provosts, dining managers, customers (enrolled dining students), and non-customers.

**Source model:** `backend/app/models/user.py` → class `User`

| Column | Type | Null | Default | Key | Description |
|--------|------|------|---------|-----|-------------|
| `id` | VARCHAR(36) | NO | UUID v4 | PK | Universally unique identifier |
| `student_id` | VARCHAR(20) | NO | — | UNI | Format: `DEPT-YEAR-SEQ` (e.g., `IRE-2001-001`) |
| `username` | VARCHAR(50) | NO | — | UNI | Lowercase login name |
| `full_name` | VARCHAR(150) | NO | — | | Display name |
| `email` | VARCHAR(255) | NO | — | UNI | Lowercase email address |
| `password_hash` | VARCHAR(255) | NO | — | | Argon2id hash |
| `role` | ENUM | NO | `NON_CUSTOMER` | IDX | `PROVOST`, `DINING_MANAGER`, `CUSTOMER`, `NON_CUSTOMER` |
| `department` | VARCHAR(100) | YES | NULL | | `IRE`, `CySE`, `DSE`, `EdTE`, `SE` |
| `batch` | VARCHAR(20) | YES | NULL | | Enrollment year (e.g., `2020`) |
| `hall_name` | VARCHAR(100) | YES | NULL | | `UFTB Boys Hall`, `UFTB Girls Hall-1`, `UFTB Girls Hall-2` |
| `phone` | VARCHAR(20) | YES | NULL | | Contact number |
| `profile_image` | VARCHAR(500) | YES | NULL | | Avatar file path |
| `status` | ENUM | NO | `INACTIVE` | IDX | `ACTIVE`, `INACTIVE`, `SUSPENDED` |
| `email_verified` | TINYINT(1) | NO | 0 | | Must be true to activate |
| `failed_attempts` | INT | NO | 0 | | Resets on successful login |
| `locked_until` | DATETIME | YES | NULL | | Set after 5 failed attempts |
| `last_login` | DATETIME | YES | NULL | | Updated on each login |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | |

---

## 2. `refresh_tokens`

**Purpose:** Stores SHA-256 hashes of JWT refresh tokens. Used for token rotation — old tokens are deleted when new ones are issued.

**Source model:** `backend/app/models/user.py` → class `RefreshToken`

| Column | Type | Null | Default | Key | Description |
|--------|------|------|---------|-----|-------------|
| `id` | VARCHAR(36) | NO | UUID v4 | PK | |
| `user_id` | VARCHAR(36) | NO | — | FK, IDX | → `users.id` (CASCADE) |
| `token_hash` | VARCHAR(255) | NO | — | UNI | SHA-256 of the JWT string |
| `expires_at` | DATETIME | NO | — | IDX | 7 days from creation |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | |

---

## 3. `meal_schedules`

**Purpose:** Defines the time windows for each meal type. Exactly 3 rows: BREAKFAST, LUNCH, DINNER. Controls when students can enroll and when the cancel deadline is.

**Source model:** `backend/app/models/meal.py` → class `MealSchedule`

| Column | Type | Null | Default | Key | Description |
|--------|------|------|---------|-----|-------------|
| `id` | VARCHAR(36) | NO | UUID v4 | PK | |
| `meal_type` | ENUM | NO | — | UNI | `BREAKFAST`, `LUNCH`, `DINNER` |
| `start_time` | TIME | NO | — | | e.g., `07:00:00` |
| `end_time` | TIME | NO | — | | e.g., `09:00:00` |
| `cancel_deadline` | TIME | NO | — | | e.g., `06:30:00` |
| `is_active` | TINYINT(1) | NO | 1 | IDX | Can be disabled by manager |
| `created_by` | VARCHAR(36) | NO | — | FK | → `users.id` |
| `updated_by` | VARCHAR(36) | YES | NULL | FK | → `users.id` |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | |

---

## 4. `daily_menus`

**Purpose:** One row per date + meal_type combination. Represents the planned menu for a specific meal on a specific day. Can be cancelled by the manager.

**Source model:** `backend/app/models/meal.py` → class `DailyMenu`

| Column | Type | Null | Default | Key | Description |
|--------|------|------|---------|-----|-------------|
| `id` | VARCHAR(36) | NO | UUID v4 | PK | |
| `date` | DATE | NO | — | IDX | Menu date |
| `meal_type` | ENUM | NO | — | | `BREAKFAST`, `LUNCH`, `DINNER` |
| `is_cancelled` | TINYINT(1) | NO | 0 | | Manager can cancel a day's meal |
| `created_by` | VARCHAR(36) | NO | — | FK | → `users.id` |
| `updated_by` | VARCHAR(36) | YES | NULL | FK | → `users.id` |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | |

**Unique constraint:** `(date, meal_type)` — one menu per date per meal type.

---

## 5. `menu_items`

**Purpose:** Individual food items belonging to a daily menu. Cascades on menu deletion.

**Source model:** `backend/app/models/meal.py` → class `MenuItem`

| Column | Type | Null | Default | Key | Description |
|--------|------|------|---------|-----|-------------|
| `id` | VARCHAR(36) | NO | UUID v4 | PK | |
| `menu_id` | VARCHAR(36) | NO | — | FK, IDX | → `daily_menus.id` (CASCADE) |
| `food_name` | VARCHAR(200) | NO | — | | e.g., "Chicken Curry" |
| `quantity` | VARCHAR(100) | YES | NULL | | e.g., "2 pieces" |
| `notes` | TEXT | YES | NULL | | Optional preparation notes |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | |

---

## 6. `student_meals`

**Purpose:** Tracks each customer's meal enrollment. One row per user + date + meal_type. Status can be ACTIVE or CANCELLED.

**Source model:** `backend/app/models/meal.py` → class `StudentMeal`

| Column | Type | Null | Default | Key | Description |
|--------|------|------|---------|-----|-------------|
| `id` | VARCHAR(36) | NO | UUID v4 | PK | |
| `user_id` | VARCHAR(36) | NO | — | FK, IDX | → `users.id` (CASCADE) |
| `date` | DATE | NO | — | IDX | Meal date |
| `meal_type` | ENUM | NO | — | | `BREAKFAST`, `LUNCH`, `DINNER` |
| `status` | ENUM | NO | `ACTIVE` | IDX | `ACTIVE`, `CANCELLED` |
| `cancelled_at` | DATETIME | YES | NULL | | Timestamp of cancellation |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | |

**Unique constraint:** `(user_id, date, meal_type)` — prevents double enrollment.

---

## 7. `payments`

**Purpose:** Payment transactions for non-customer meal requests. Tracks method, reference number, and status.

**Source model:** `backend/app/models/expense.py` → class `Payment`

| Column | Type | Null | Default | Key | Description |
|--------|------|------|---------|-----|-------------|
| `id` | VARCHAR(36) | NO | UUID v4 | PK | |
| `user_id` | VARCHAR(36) | NO | — | FK, IDX | → `users.id` |
| `request_id` | VARCHAR(36) | YES | NULL | | Informational back-reference |
| `amount` | DECIMAL(10,2) | NO | — | | Payment amount in BDT |
| `payment_method` | ENUM | NO | — | | `CASH`, `MOBILE_BANKING`, `BANK_TRANSFER`, `OTHER` |
| `reference_no` | VARCHAR(100) | YES | NULL | | Transaction reference |
| `status` | ENUM | NO | `PENDING` | IDX | `PENDING`, `COMPLETED`, `FAILED`, `REFUNDED` |
| `note` | TEXT | YES | NULL | | Optional note |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | IDX | |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | |

---

## 8. `meal_requests`

**Purpose:** Non-customer one-time meal requests with a multi-step approval workflow: PENDING_PAYMENT → PENDING_APPROVAL → APPROVED/REJECTED.

**Source model:** `backend/app/models/expense.py` → class `MealRequest`

| Column | Type | Null | Default | Key | Description |
|--------|------|------|---------|-----|-------------|
| `id` | VARCHAR(36) | NO | UUID v4 | PK | |
| `user_id` | VARCHAR(36) | NO | — | FK, IDX | → `users.id` (requester) |
| `date` | DATE | NO | — | IDX | Requested meal date |
| `meal_type` | ENUM | NO | — | | `BREAKFAST`, `LUNCH`, `DINNER` |
| `reason` | TEXT | YES | NULL | | Justification text |
| `status` | ENUM | NO | `PENDING_PAYMENT` | IDX | 5-state workflow |
| `payment_id` | VARCHAR(36) | YES | NULL | FK | → `payments.id` |
| `reviewed_by` | VARCHAR(36) | YES | NULL | FK | → `users.id` (reviewer) |
| `reviewed_at` | DATETIME | YES | NULL | | When review happened |
| `rejection_note` | TEXT | YES | NULL | | Reason for rejection |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | |

---

## 9. `expenses`

**Purpose:** Dining hall operational expenses. Categorized for financial reporting.

**Source model:** `backend/app/models/expense.py` → class `Expense`

| Column | Type | Null | Default | Key | Description |
|--------|------|------|---------|-----|-------------|
| `id` | VARCHAR(36) | NO | UUID v4 | PK | |
| `name` | VARCHAR(200) | NO | — | | Expense description |
| `category` | ENUM | NO | — | IDX | 6 categories |
| `amount` | DECIMAL(12,2) | NO | — | | Amount in BDT |
| `description` | TEXT | YES | NULL | | Detailed notes |
| `expense_date` | DATE | NO | — | IDX | When the expense occurred |
| `created_by` | VARCHAR(36) | NO | — | FK, IDX | → `users.id` |
| `updated_by` | VARCHAR(36) | YES | NULL | FK | → `users.id` |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | |

---

## 10. `earnings`

**Purpose:** Income records from meal payments, deposits, grants, and other sources.

**Source model:** `backend/app/models/expense.py` → class `Earning`

| Column | Type | Null | Default | Key | Description |
|--------|------|------|---------|-----|-------------|
| `id` | VARCHAR(36) | NO | UUID v4 | PK | |
| `description` | VARCHAR(200) | NO | — | | Earning description |
| `category` | ENUM | NO | — | IDX | `MEAL_PAYMENT`, `DEPOSIT`, `GRANT`, `OTHER` |
| `amount` | DECIMAL(12,2) | NO | — | | Amount in BDT |
| `earning_date` | DATE | NO | — | IDX | When income was received |
| `notes` | TEXT | YES | NULL | | Additional details |
| `created_by` | VARCHAR(36) | NO | — | FK, IDX | → `users.id` |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | |

---

## 11. `member_payments`

**Purpose:** Monthly billing records for each enrolled customer. Manager initializes records in bulk; students submit proofs; manager marks as paid.

**Source model:** `backend/app/models/expense.py` → class `MemberPayment`

| Column | Type | Null | Default | Key | Description |
|--------|------|------|---------|-----|-------------|
| `id` | VARCHAR(36) | NO | UUID v4 | PK | |
| `user_id` | VARCHAR(36) | NO | — | FK, IDX | → `users.id` (CASCADE) |
| `year` | INT | NO | — | | Billing year |
| `month` | INT | NO | — | | Billing month (1-12) |
| `amount_due` | DECIMAL(12,2) | NO | 0.00 | | Total amount owed |
| `amount_paid` | DECIMAL(12,2) | NO | 0.00 | | Total amount received |
| `status` | ENUM | NO | `PENDING` | IDX | `PAID`, `PENDING` |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | |

**Unique constraint:** `(user_id, year, month)` — one record per student per month.

---

## 12. `payment_proofs`

**Purpose:** Evidence submitted by customers to verify their monthly dining payments. Can be a transaction ID, image URL, or text note.

**Source model:** `backend/app/models/expense.py` → class `PaymentProof`

| Column | Type | Null | Default | Key | Description |
|--------|------|------|---------|-----|-------------|
| `id` | VARCHAR(36) | NO | UUID v4 | PK | |
| `member_payment_id` | VARCHAR(36) | NO | — | FK, IDX | → `member_payments.id` (CASCADE) |
| `user_id` | VARCHAR(36) | NO | — | FK, IDX | → `users.id` (submitter) |
| `proof_type` | ENUM | NO | — | | `IMAGE`, `TRANSACTION_ID`, `TEXT_NOTE` |
| `proof_value` | TEXT | NO | — | | The actual proof content |
| `status` | ENUM | NO | `SUBMITTED` | IDX | `SUBMITTED`, `APPROVED`, `REJECTED` |
| `reviewed_by` | VARCHAR(36) | YES | NULL | FK | → `users.id` (reviewer) |
| `reviewed_at` | DATETIME | YES | NULL | | When review happened |
| `rejection_note` | TEXT | YES | NULL | | Reason if rejected |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | |

---

## 13. `audit_logs`

**Purpose:** Immutable record of all significant system actions. Stores old and new values as JSON for change tracking. User FK uses SET NULL so logs survive user deletion.

**Source model:** `backend/app/models/expense.py` → class `AuditLog`

| Column | Type | Null | Default | Key | Description |
|--------|------|------|---------|-----|-------------|
| `id` | BIGINT | NO | AUTO_INCREMENT | PK | Sequential ID |
| `user_id` | VARCHAR(36) | YES | NULL | FK, IDX | → `users.id` (SET NULL) |
| `action` | VARCHAR(100) | NO | — | IDX | e.g., `MEAL_ADDED`, `EXPENSE_CREATED` |
| `entity_type` | VARCHAR(50) | NO | — | IDX | e.g., `User`, `StudentMeal`, `Expense` |
| `entity_id` | VARCHAR(36) | YES | NULL | IDX | UUID of affected entity |
| `old_value` | JSON | YES | NULL | | Previous state (for updates) |
| `new_value` | JSON | YES | NULL | | New state |
| `ip_address` | VARCHAR(45) | YES | NULL | | Client IP (supports IPv6) |
| `user_agent` | VARCHAR(500) | YES | NULL | | Browser/client identifier |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | IDX | |

---

## 14. `system_settings`

**Purpose:** Key-value configuration store for runtime settings. Allows the provost to change application behavior without redeployment.

**Source model:** `backend/app/models/expense.py` → class `SystemSetting`

| Column | Type | Null | Default | Key | Description |
|--------|------|------|---------|-----|-------------|
| `id` | BIGINT | NO | AUTO_INCREMENT | PK | |
| `key_name` | VARCHAR(100) | NO | — | UNI | Setting identifier |
| `value` | TEXT | NO | — | | Setting value (stored as text) |
| `description` | VARCHAR(500) | YES | NULL | | Human-readable explanation |
| `updated_by` | VARCHAR(36) | YES | NULL | FK | → `users.id` |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | |

**Default settings:** `meal_price_non_customer`, `max_meals_per_day`, `allow_same_day_requests`, `auto_approve_requests`, `site_name`, `academic_year`, `contact_email`, `notice_board`
