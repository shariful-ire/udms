# UDMS — MySQL / XAMPP Setup Guide

## Prerequisites

- **XAMPP** installed (version 8.0+ recommended) — [Download](https://www.apachefriends.org/)
- MySQL 8.0 is included with XAMPP
- phpMyAdmin is included with XAMPP

---

## Step 1: Start XAMPP Services

1. Open **XAMPP Control Panel**
2. Click **Start** next to **Apache** (required for phpMyAdmin)
3. Click **Start** next to **MySQL**
4. Verify both show green "Running" status

---

## Step 2: Import the Database Schema

### Option A: Via phpMyAdmin (GUI)

1. Open your browser and go to: **http://localhost/phpmyadmin**
2. Click the **Import** tab at the top
3. Click **Choose File** and select: `database_export/udms_database.sql`
4. Ensure the following settings:
   - Character set: **utf-8**
   - Format: **SQL**
5. Click **Go** / **Import**
6. You should see: *"14 tables created successfully"*

### Option B: Via MySQL Command Line

```bash
# Open XAMPP Shell or Command Prompt
cd C:\xampp\mysql\bin

# Import the schema
mysql -u root -p < "path\to\database_export\udms_database.sql"

# When prompted for password, press Enter (XAMPP default has no password)
```

### Option C: Via MySQL Command (if password is set)

```bash
mysql -u root -p"your_password" < "path\to\database_export\udms_database.sql"
```

---

## Step 3: Import Sample Data

After the schema is created, import the sample data:

### Via phpMyAdmin:
1. In phpMyAdmin, select the **udms** database from the left sidebar
2. Click the **Import** tab
3. Choose file: `database_export/sample_data.sql`
4. Click **Go**

### Via Command Line:
```bash
mysql -u root -p udms < "path\to\database_export\sample_data.sql"
```

---

## Step 4: Verify the Installation

### In phpMyAdmin:
1. Click on the **udms** database in the left sidebar
2. You should see **14 tables** listed:
   - `audit_logs`
   - `daily_menus`
   - `earnings`
   - `expenses`
   - `meal_requests`
   - `meal_schedules`
   - `member_payments`
   - `menu_items`
   - `payment_proofs`
   - `payments`
   - `refresh_tokens`
   - `student_meals`
   - `system_settings`
   - `users`

3. Click on the **users** table — you should see 6 sample users
4. Click on the **SQL** tab and run:
   ```sql
   SELECT COUNT(*) AS table_count
   FROM information_schema.tables
   WHERE table_schema = 'udms';
   ```
   Expected result: `14`

### Verify foreign keys:
```sql
SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'udms' AND REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY TABLE_NAME;
```
Expected: **20 foreign key relationships**

---

## Step 5: Run Example Queries

You can now run any of the provided SQL files:

| File | Purpose | How to Run |
|------|---------|------------|
| `crud_examples.sql` | CRUD operations for all 14 tables | Copy individual queries into phpMyAdmin SQL tab |
| `join_examples.sql` | JOIN queries across related tables | Copy individual queries |
| `aggregate_queries.sql` | GROUP BY, SUM, AVG, reports | Copy individual queries |

**Important:** Run queries one at a time from the SQL tab. Do not import the entire file at once — the example files contain SELECT queries mixed with INSERT/UPDATE/DELETE and are meant for learning, not batch execution.

---

## Troubleshooting

### Error: "Access denied for user 'root'@'localhost'"
- XAMPP default MySQL has no password. Just press Enter when prompted.
- If you set a password, use: `mysql -u root -p"your_password"`

### Error: "Can't create database 'udms'; database exists"
- The schema uses `CREATE DATABASE IF NOT EXISTS`, so this shouldn't happen.
- If you want a fresh start:
  ```sql
  DROP DATABASE IF EXISTS udms;
  ```
  Then re-import `udms_database.sql`.

### Error: "Cannot add foreign key constraint"
- The schema uses `SET FOREIGN_KEY_CHECKS = 0` at the start, so table order doesn't matter.
- If you still get errors, ensure you're using MySQL 8.0+ (check with `SELECT VERSION();`).

### Error: "Specified key was too long"
- This happens with `utf8mb4` if the index key exceeds 3072 bytes.
- Ensure your MySQL config has: `innodb_large_prefix=ON` (default in MySQL 8.0).

### phpMyAdmin shows garbled characters
- Ensure the database collation is `utf8mb4_unicode_ci`.
- In phpMyAdmin, go to Operations → Collation → set to `utf8mb4_unicode_ci`.

### XAMPP MySQL won't start
- Check if port 3306 is already in use (another MySQL instance, etc.).
- Open XAMPP Config → MySQL → change port if needed.

---

## Optional: Create a Dedicated User

Instead of using root, create a dedicated user for UDMS:

```sql
CREATE USER 'udms_user'@'localhost' IDENTIFIED BY 'udms_password_123';
GRANT ALL PRIVILEGES ON udms.* TO 'udms_user'@'localhost';
FLUSH PRIVILEGES;
```

---

## File Summary

| File | Description | Import Order |
|------|-------------|-------------|
| `udms_database.sql` | Complete schema (14 tables, all constraints) | **1st** — required |
| `sample_data.sql` | Sample data (users, menus, meals, expenses, etc.) | **2nd** — optional |
| `crud_examples.sql` | CRUD operations for every table | Reference only |
| `join_examples.sql` | JOIN queries using real relationships | Reference only |
| `aggregate_queries.sql` | GROUP BY, SUM, AVG, dashboard/report queries | Reference only |
| `relationships.md` | Foreign key documentation | Documentation |
| `er_diagram.md` | Mermaid ER diagram + workflow diagrams | Documentation |
| `table_descriptions.md` | Detailed column descriptions for all 14 tables | Documentation |
| `database_documentation.md` | Complete database analysis and normalization | Documentation |
| `mysql_xampp_setup.md` | This file — setup instructions | Documentation |
