-- ============================================================================
-- UDMS — Aggregate Queries (GROUP BY, COUNT, SUM, AVG, Reports)
-- ============================================================================
-- Real-world analytical queries for dashboards and financial reports.
-- ============================================================================

USE `udms`;


-- ============================================================================
-- 1. COUNT Queries
-- ============================================================================

-- 1a. User count by role
SELECT role, COUNT(*) AS user_count
FROM `users`
GROUP BY role
ORDER BY FIELD(role, 'PROVOST', 'DINING_MANAGER', 'CUSTOMER', 'NON_CUSTOMER');

-- 1b. User count by status
SELECT status, COUNT(*) AS user_count
FROM `users`
GROUP BY status;

-- 1c. User count by department
SELECT department, COUNT(*) AS student_count
FROM `users`
WHERE role IN ('CUSTOMER', 'NON_CUSTOMER')
GROUP BY department
ORDER BY student_count DESC;

-- 1d. User count by hall
SELECT hall_name, COUNT(*) AS resident_count
FROM `users`
WHERE hall_name IS NOT NULL
GROUP BY hall_name
ORDER BY resident_count DESC;

-- 1e. Daily meal enrollment count
SELECT date, meal_type,
       COUNT(*) AS total_enrolled,
       SUM(CASE WHEN status = 'ACTIVE' THEN 1 ELSE 0 END) AS active,
       SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END) AS cancelled
FROM `student_meals`
GROUP BY date, meal_type
ORDER BY date DESC, FIELD(meal_type, 'BREAKFAST', 'LUNCH', 'DINNER');

-- 1f. Meal request status distribution
SELECT status, COUNT(*) AS request_count
FROM `meal_requests`
GROUP BY status
ORDER BY request_count DESC;

-- 1g. Payment proof status distribution
SELECT status, COUNT(*) AS proof_count
FROM `payment_proofs`
GROUP BY status;

-- 1h. Expense count by category
SELECT category, COUNT(*) AS expense_count
FROM `expenses`
GROUP BY category
ORDER BY expense_count DESC;

-- 1i. Number of menu items per meal type (across all dates)
SELECT dm.meal_type, COUNT(mi.id) AS total_items
FROM `daily_menus` dm
LEFT JOIN `menu_items` mi ON dm.id = mi.menu_id
GROUP BY dm.meal_type;


-- ============================================================================
-- 2. SUM Queries
-- ============================================================================

-- 2a. Total expenses by category
SELECT category,
       SUM(amount) AS total_amount,
       COUNT(*) AS transaction_count
FROM `expenses`
GROUP BY category
ORDER BY total_amount DESC;

-- 2b. Total earnings by category
SELECT category,
       SUM(amount) AS total_amount,
       COUNT(*) AS transaction_count
FROM `earnings`
GROUP BY category
ORDER BY total_amount DESC;

-- 2c. Total expenses vs total earnings (net balance)
SELECT
  (SELECT COALESCE(SUM(amount), 0) FROM `expenses`)  AS total_expenses,
  (SELECT COALESCE(SUM(amount), 0) FROM `earnings`)  AS total_earnings,
  (SELECT COALESCE(SUM(amount), 0) FROM `earnings`) -
  (SELECT COALESCE(SUM(amount), 0) FROM `expenses`)  AS net_balance;

-- 2d. Monthly expense totals
SELECT YEAR(expense_date) AS yr, MONTH(expense_date) AS mo,
       SUM(amount) AS monthly_total
FROM `expenses`
GROUP BY YEAR(expense_date), MONTH(expense_date)
ORDER BY yr DESC, mo DESC;

-- 2e. Monthly earning totals
SELECT YEAR(earning_date) AS yr, MONTH(earning_date) AS mo,
       SUM(amount) AS monthly_total
FROM `earnings`
GROUP BY YEAR(earning_date), MONTH(earning_date)
ORDER BY yr DESC, mo DESC;

-- 2f. Total amount due vs paid per month (member payments)
SELECT year, month,
       SUM(amount_due)  AS total_due,
       SUM(amount_paid) AS total_paid,
       SUM(amount_due) - SUM(amount_paid) AS outstanding
FROM `member_payments`
GROUP BY year, month
ORDER BY year DESC, month DESC;

-- 2g. Payment revenue by method
SELECT payment_method,
       SUM(amount) AS total_collected,
       COUNT(*)    AS transaction_count
FROM `payments`
WHERE status = 'COMPLETED'
GROUP BY payment_method
ORDER BY total_collected DESC;


-- ============================================================================
-- 3. AVG Queries
-- ============================================================================

-- 3a. Average expense per category
SELECT category,
       AVG(amount) AS avg_amount,
       MIN(amount) AS min_amount,
       MAX(amount) AS max_amount
FROM `expenses`
GROUP BY category
ORDER BY avg_amount DESC;

-- 3b. Average earning per category
SELECT category,
       AVG(amount)   AS avg_amount,
       MIN(amount)   AS min_amount,
       MAX(amount)   AS max_amount
FROM `earnings`
GROUP BY category;

-- 3c. Average meals per customer per day
SELECT
  COUNT(*) AS total_meal_records,
  COUNT(DISTINCT user_id) AS unique_customers,
  COUNT(DISTINCT date)    AS unique_days,
  ROUND(COUNT(*) / COUNT(DISTINCT user_id), 2) AS avg_meals_per_customer,
  ROUND(COUNT(*) / COUNT(DISTINCT date), 2)    AS avg_meals_per_day
FROM `student_meals`
WHERE status = 'ACTIVE';

-- 3d. Average daily expense
SELECT
  ROUND(AVG(daily_total), 2) AS avg_daily_expense
FROM (
  SELECT expense_date, SUM(amount) AS daily_total
  FROM `expenses`
  GROUP BY expense_date
) daily_expenses;

-- 3e. Average payment amount for non-customer requests
SELECT
  ROUND(AVG(amount), 2) AS avg_payment,
  MIN(amount) AS min_payment,
  MAX(amount) AS max_payment
FROM `payments`
WHERE status = 'COMPLETED';


-- ============================================================================
-- 4. Monthly Report Queries (as used by the UDMS dashboard)
-- ============================================================================

-- 4a. MONTHLY FINANCIAL REPORT: Income, Expenses, Net for a given month
SELECT
  '2026-06' AS report_month,
  COALESCE(exp.total, 0) AS total_expenses,
  COALESCE(ear.total, 0) AS total_earnings,
  COALESCE(ear.total, 0) - COALESCE(exp.total, 0) AS net_balance
FROM
  (SELECT SUM(amount) AS total FROM `expenses`
   WHERE expense_date BETWEEN '2026-06-01' AND '2026-06-30') exp,
  (SELECT SUM(amount) AS total FROM `earnings`
   WHERE earning_date BETWEEN '2026-06-01' AND '2026-06-30') ear;


-- 4b. MONTHLY EXPENSE BREAKDOWN by category
SELECT category,
       SUM(amount) AS category_total,
       ROUND(SUM(amount) * 100.0 /
         (SELECT SUM(amount) FROM `expenses`
          WHERE expense_date BETWEEN '2026-06-01' AND '2026-06-30'), 1
       ) AS percentage
FROM `expenses`
WHERE expense_date BETWEEN '2026-06-01' AND '2026-06-30'
GROUP BY category
ORDER BY category_total DESC;


-- 4c. MONTHLY MEAL BREAKDOWN (breakfast/lunch/dinner counts)
SELECT
  meal_type,
  COUNT(*)  AS total_enrolled,
  SUM(CASE WHEN status = 'ACTIVE'    THEN 1 ELSE 0 END) AS consumed,
  SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END) AS cancelled,
  ROUND(SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1)
    AS cancellation_rate_pct
FROM `student_meals`
WHERE date BETWEEN '2026-06-01' AND '2026-06-30'
GROUP BY meal_type
ORDER BY FIELD(meal_type, 'BREAKFAST', 'LUNCH', 'DINNER');


-- 4d. MONTHLY PER-MEAL COST calculation
SELECT
  COALESCE(SUM(e.amount), 0) AS total_expenses,
  COALESCE(meal_counts.consumed, 0) AS total_consumed_meals,
  CASE
    WHEN COALESCE(meal_counts.consumed, 0) > 0
    THEN ROUND(SUM(e.amount) / meal_counts.consumed, 2)
    ELSE 0
  END AS per_meal_cost
FROM `expenses` e,
(
  SELECT COUNT(*) AS consumed
  FROM `student_meals`
  WHERE date BETWEEN '2026-06-01' AND '2026-06-30'
    AND status = 'ACTIVE'
) meal_counts
WHERE e.expense_date BETWEEN '2026-06-01' AND '2026-06-30';


-- 4e. MONTHLY MEMBER PAYMENT SUMMARY
SELECT
  COUNT(*) AS total_members,
  SUM(CASE WHEN status = 'PAID'    THEN 1 ELSE 0 END) AS paid_count,
  SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) AS pending_count,
  SUM(amount_due)  AS total_due,
  SUM(amount_paid) AS total_collected,
  SUM(amount_due) - SUM(amount_paid) AS outstanding_balance
FROM `member_payments`
WHERE year = 2026 AND month = 6;


-- 4f. DAILY REPORT: Meals served + expenses for a specific date
SELECT
  '2026-06-24' AS report_date,
  (SELECT COUNT(*) FROM `student_meals`
   WHERE date = '2026-06-24' AND status = 'ACTIVE') AS meals_served,
  (SELECT COUNT(*) FROM `student_meals`
   WHERE date = '2026-06-24' AND status = 'CANCELLED') AS meals_cancelled,
  (SELECT COALESCE(SUM(amount), 0) FROM `expenses`
   WHERE expense_date = '2026-06-24') AS day_expenses;


-- 4g. WEEKLY REPORT: 7-day meal session summary
SELECT
  active_customers.count AS active_customer_count,
  active_customers.count * 3 * 7 AS total_possible_meals,
  COALESCE(consumed.count, 0) AS consumed_meals,
  (active_customers.count * 3 * 7 - COALESCE(consumed.count, 0)) AS remaining_meals,
  COALESCE(week_exp.total, 0) AS week_expenses,
  CASE
    WHEN COALESCE(consumed.count, 0) > 0
    THEN ROUND(COALESCE(week_exp.total, 0) / consumed.count, 2)
    ELSE 0
  END AS per_meal_cost
FROM
  (SELECT COUNT(*) AS count FROM `users`
   WHERE role = 'CUSTOMER' AND status = 'ACTIVE') active_customers,
  (SELECT COUNT(*) AS count FROM `student_meals`
   WHERE date BETWEEN DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND CURDATE()
     AND status = 'ACTIVE') consumed,
  (SELECT SUM(amount) AS total FROM `expenses`
   WHERE expense_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND CURDATE()) week_exp;


-- 4h. YEARLY REPORT: Month-by-month comparison
SELECT
  MONTH(e.expense_date) AS month_num,
  MONTHNAME(e.expense_date) AS month_name,
  SUM(e.amount) AS monthly_expenses
FROM `expenses` e
WHERE YEAR(e.expense_date) = 2026
GROUP BY MONTH(e.expense_date), MONTHNAME(e.expense_date)
ORDER BY month_num;


-- ============================================================================
-- 5. DASHBOARD STATISTICS (as computed by GET /dashboard/stats)
-- ============================================================================

-- 5a. Dashboard aggregated stats
SELECT
  (SELECT COALESCE(SUM(amount), 0) FROM `expenses`)  AS total_expenses,
  (SELECT COALESCE(SUM(amount), 0) FROM `earnings`)  AS total_earnings,
  (SELECT COALESCE(SUM(amount), 0) FROM `earnings`) -
  (SELECT COALESCE(SUM(amount), 0) FROM `expenses`)  AS net_balance,
  (SELECT COUNT(*) FROM `users`
   WHERE role = 'CUSTOMER' AND status = 'ACTIVE')    AS active_customers,
  (SELECT COUNT(*) FROM `users`
   WHERE status = 'ACTIVE')                           AS total_active_users,
  (SELECT COUNT(*) FROM `meal_requests`
   WHERE status = 'PENDING_APPROVAL')                 AS pending_requests,
  (SELECT COUNT(*) FROM `payment_proofs`
   WHERE status = 'SUBMITTED')                        AS pending_proofs;


-- 5b. Top expense categories this month
SELECT category, SUM(amount) AS total
FROM `expenses`
WHERE YEAR(expense_date) = YEAR(CURDATE()) AND MONTH(expense_date) = MONTH(CURDATE())
GROUP BY category
ORDER BY total DESC
LIMIT 5;


-- 5c. Meal attendance trend (last 7 days)
SELECT date,
       COUNT(*) AS total,
       SUM(CASE WHEN status = 'ACTIVE' THEN 1 ELSE 0 END) AS consumed,
       SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END) AS cancelled
FROM `student_meals`
WHERE date BETWEEN DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND CURDATE()
GROUP BY date
ORDER BY date;


-- 5d. Department-wise customer distribution
SELECT u.department,
       COUNT(*) AS customer_count,
       ROUND(COUNT(*) * 100.0 /
         (SELECT COUNT(*) FROM `users` WHERE role = 'CUSTOMER'), 1) AS percentage
FROM `users` u
WHERE u.role = 'CUSTOMER'
GROUP BY u.department
ORDER BY customer_count DESC;


-- 5e. Recent audit activity (last 24 hours)
SELECT action, COUNT(*) AS count
FROM `audit_logs`
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY action
ORDER BY count DESC;
