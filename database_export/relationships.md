# UDMS — Foreign Key Relationships

> Extracted from SQLAlchemy models: `backend/app/models/user.py`, `meal.py`, `expense.py`

## All Foreign Keys (20 total)

| # | Source Table | Source Column | Target Table | Target Column | ON DELETE | Purpose |
|---|-------------|---------------|-------------|---------------|-----------|---------|
| 1 | `refresh_tokens` | `user_id` | `users` | `id` | **CASCADE** | User's active sessions |
| 2 | `meal_schedules` | `created_by` | `users` | `id` | RESTRICT | Who created the schedule |
| 3 | `meal_schedules` | `updated_by` | `users` | `id` | RESTRICT | Who last modified it |
| 4 | `daily_menus` | `created_by` | `users` | `id` | RESTRICT | Who created the menu |
| 5 | `daily_menus` | `updated_by` | `users` | `id` | RESTRICT | Who last modified it |
| 6 | `menu_items` | `menu_id` | `daily_menus` | `id` | **CASCADE** | Which menu this item belongs to |
| 7 | `student_meals` | `user_id` | `users` | `id` | **CASCADE** | Which student enrolled for this meal |
| 8 | `payments` | `user_id` | `users` | `id` | RESTRICT | Who made the payment |
| 9 | `meal_requests` | `user_id` | `users` | `id` | RESTRICT | Who submitted the request |
| 10 | `meal_requests` | `payment_id` | `payments` | `id` | RESTRICT | Associated payment for this request |
| 11 | `meal_requests` | `reviewed_by` | `users` | `id` | RESTRICT | Manager who reviewed |
| 12 | `expenses` | `created_by` | `users` | `id` | RESTRICT | Who logged the expense |
| 13 | `expenses` | `updated_by` | `users` | `id` | RESTRICT | Who last edited it |
| 14 | `earnings` | `created_by` | `users` | `id` | RESTRICT | Who recorded the earning |
| 15 | `member_payments` | `user_id` | `users` | `id` | **CASCADE** | Which customer this billing is for |
| 16 | `payment_proofs` | `member_payment_id` | `member_payments` | `id` | **CASCADE** | Which billing record |
| 17 | `payment_proofs` | `user_id` | `users` | `id` | RESTRICT | Who submitted the proof |
| 18 | `payment_proofs` | `reviewed_by` | `users` | `id` | RESTRICT | Who reviewed the proof |
| 19 | `audit_logs` | `user_id` | `users` | `id` | **SET NULL** | Who performed the action |
| 20 | `system_settings` | `updated_by` | `users` | `id` | RESTRICT | Who last changed the setting |

## ON DELETE Behavior Summary

| Rule | Tables Affected | Reason |
|------|----------------|--------|
| **CASCADE** | `refresh_tokens`, `student_meals`, `member_payments`, `payment_proofs`, `menu_items` | Child records have no meaning without the parent |
| **SET NULL** | `audit_logs` | Preserve the log entry even if the user is deleted |
| **RESTRICT** (default) | `expenses`, `earnings`, `meal_requests`, `payments`, `meal_schedules`, `daily_menus`, `system_settings` | Prevent accidental deletion of users who have financial records |

## Cardinality

| Relationship | Cardinality | Constraint |
|-------------|-------------|------------|
| `users` ↔ `refresh_tokens` | 1 : N | One user can have multiple active sessions |
| `users` ↔ `student_meals` | 1 : N | One customer has many meal records; UNIQUE on (user_id, date, meal_type) |
| `users` ↔ `meal_requests` | 1 : N | One non-customer can submit many requests |
| `users` ↔ `payments` | 1 : N | One user can make many payments |
| `users` ↔ `member_payments` | 1 : N | One customer has one billing record per month; UNIQUE on (user_id, year, month) |
| `users` ↔ `expenses` | 1 : N | One manager creates many expenses |
| `users` ↔ `earnings` | 1 : N | One manager records many earnings |
| `users` ↔ `audit_logs` | 1 : N | One user generates many audit entries |
| `daily_menus` ↔ `menu_items` | 1 : N | One menu has many food items |
| `meal_requests` ↔ `payments` | N : 1 | Many requests can reference the same payment (bulk payment) |
| `member_payments` ↔ `payment_proofs` | 1 : N | One billing record can have multiple proof submissions |

## Unique Constraints (9 total)

| Table | Columns | Constraint Name | Purpose |
|-------|---------|-----------------|---------|
| `users` | `student_id` | `uq_users_student_id` | No duplicate student IDs |
| `users` | `username` | `uq_users_username` | No duplicate usernames |
| `users` | `email` | `uq_users_email` | No duplicate emails |
| `meal_schedules` | `meal_type` | `uq_ms_meal_type` | Only one schedule per meal type |
| `daily_menus` | `(date, meal_type)` | `uq_date_meal_type` | Only one menu per date + meal type |
| `student_meals` | `(user_id, date, meal_type)` | `uq_user_date_meal` | A student can enroll once per date + meal type |
| `member_payments` | `(user_id, year, month)` | `uq_user_year_month` | One billing record per student per month |
| `refresh_tokens` | `token_hash` | `uq_rt_token_hash` | No duplicate tokens |
| `system_settings` | `key_name` | `uq_ss_key_name` | No duplicate setting keys |

## FK Dependency Graph

```
users (root — no FK dependencies)
  ├── refresh_tokens         (CASCADE)
  ├── meal_schedules         (created_by, updated_by)
  ├── daily_menus            (created_by, updated_by)
  │     └── menu_items       (CASCADE)
  ├── student_meals          (CASCADE)
  ├── payments               (user_id)
  │     └── meal_requests    (payment_id, user_id, reviewed_by)
  ├── expenses               (created_by, updated_by)
  ├── earnings               (created_by)
  ├── member_payments        (CASCADE)
  │     └── payment_proofs   (CASCADE, user_id, reviewed_by)
  ├── audit_logs             (SET NULL)
  └── system_settings        (updated_by)
```
