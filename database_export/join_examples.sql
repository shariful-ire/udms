-- ============================================================================
-- UDMS — JOIN Query Examples
-- ============================================================================
-- Real-world queries using actual foreign key relationships between tables.
-- Each query is annotated with the relationship it exercises.
-- ============================================================================

USE `udms`;


-- ============================================================================
-- 1. INNER JOINS (matching records in both tables)
-- ============================================================================

-- 1a. Users + Student Meals: Get all active meals with student details
--     Relationship: student_meals.user_id → users.id
SELECT u.full_name, u.student_id, u.department,
       sm.date, sm.meal_type, sm.status
FROM `student_meals` sm
INNER JOIN `users` u ON sm.user_id = u.id
WHERE sm.status = 'ACTIVE'
ORDER BY sm.date DESC, u.full_name;


-- 1b. Daily Menus + Menu Items: Get complete menu with food items
--     Relationship: menu_items.menu_id → daily_menus.id
SELECT dm.date, dm.meal_type, dm.is_cancelled,
       mi.food_name, mi.quantity, mi.notes
FROM `daily_menus` dm
INNER JOIN `menu_items` mi ON dm.id = mi.menu_id
WHERE dm.date = '2026-06-24'
ORDER BY FIELD(dm.meal_type, 'BREAKFAST', 'LUNCH', 'DINNER'), mi.food_name;


-- 1c. Meal Requests + Users + Payments: Request details with requester and payment info
--     Relationships: meal_requests.user_id → users.id
--                    meal_requests.payment_id → payments.id
SELECT mr.date, mr.meal_type, mr.status AS request_status,
       u.full_name AS requester, u.student_id, u.department,
       p.amount, p.payment_method, p.reference_no, p.status AS payment_status
FROM `meal_requests` mr
INNER JOIN `users` u ON mr.user_id = u.id
INNER JOIN `payments` p ON mr.payment_id = p.id
ORDER BY mr.date;


-- 1d. Member Payments + Users: Payment tracking with student info
--     Relationship: member_payments.user_id → users.id
SELECT u.full_name, u.student_id, u.department,
       mp.year, mp.month, mp.amount_due, mp.amount_paid, mp.status,
       (mp.amount_due - mp.amount_paid) AS balance_remaining
FROM `member_payments` mp
INNER JOIN `users` u ON mp.user_id = u.id
WHERE mp.year = 2026 AND mp.month = 6
ORDER BY mp.status DESC, u.full_name;


-- 1e. Payment Proofs + Member Payments + Users: Proof review dashboard
--     Relationships: payment_proofs.member_payment_id → member_payments.id
--                    payment_proofs.user_id → users.id
SELECT u.full_name, u.student_id,
       mp.year, mp.month, mp.amount_due,
       pp.proof_type, pp.proof_value, pp.status AS proof_status
FROM `payment_proofs` pp
INNER JOIN `member_payments` mp ON pp.member_payment_id = mp.id
INNER JOIN `users` u ON pp.user_id = u.id
ORDER BY pp.created_at DESC;


-- 1f. Expenses + Users (creator): Expense list with who created it
--     Relationship: expenses.created_by → users.id
SELECT e.name, e.category, e.amount, e.expense_date,
       u.full_name AS created_by_name
FROM `expenses` e
INNER JOIN `users` u ON e.created_by = u.id
ORDER BY e.expense_date DESC;


-- 1g. Earnings + Users (creator): Earnings with creator info
--     Relationship: earnings.created_by → users.id
SELECT ea.description, ea.category, ea.amount, ea.earning_date,
       u.full_name AS recorded_by
FROM `earnings` ea
INNER JOIN `users` u ON ea.created_by = u.id
ORDER BY ea.earning_date DESC;


-- 1h. Audit Logs + Users: Activity log with actor details
--     Relationship: audit_logs.user_id → users.id
SELECT al.action, al.entity_type, al.entity_id,
       u.full_name AS actor, u.role,
       al.ip_address, al.created_at
FROM `audit_logs` al
INNER JOIN `users` u ON al.user_id = u.id
ORDER BY al.created_at DESC;


-- ============================================================================
-- 2. LEFT JOINS (include records even without matches)
-- ============================================================================

-- 2a. Users LEFT JOIN Student Meals: All customers including those with no meals today
SELECT u.full_name, u.student_id,
       sm.meal_type, sm.status AS meal_status
FROM `users` u
LEFT JOIN `student_meals` sm ON u.id = sm.user_id AND sm.date = CURDATE()
WHERE u.role = 'CUSTOMER' AND u.status = 'ACTIVE'
ORDER BY u.full_name;


-- 2b. Daily Menus LEFT JOIN Menu Items: Show menus even if no items added yet
SELECT dm.date, dm.meal_type, dm.is_cancelled,
       COALESCE(GROUP_CONCAT(mi.food_name SEPARATOR ', '), '(no items)') AS food_items
FROM `daily_menus` dm
LEFT JOIN `menu_items` mi ON dm.id = mi.menu_id
WHERE dm.date BETWEEN '2026-06-23' AND '2026-06-25'
GROUP BY dm.id, dm.date, dm.meal_type, dm.is_cancelled
ORDER BY dm.date, FIELD(dm.meal_type, 'BREAKFAST', 'LUNCH', 'DINNER');


-- 2c. Meal Requests LEFT JOIN Payments: Show all requests including unpaid ones
SELECT mr.date, mr.meal_type, mr.reason, mr.status,
       u.full_name AS requester,
       COALESCE(p.amount, 0) AS paid_amount,
       COALESCE(p.payment_method, 'NOT PAID') AS method
FROM `meal_requests` mr
INNER JOIN `users` u ON mr.user_id = u.id
LEFT JOIN `payments` p ON mr.payment_id = p.id
ORDER BY mr.date DESC;


-- 2d. Meal Requests LEFT JOIN Reviewer: Show requests with optional reviewer info
SELECT mr.date, mr.meal_type, mr.status,
       req.full_name AS requester,
       rev.full_name AS reviewed_by_name,
       mr.reviewed_at, mr.rejection_note
FROM `meal_requests` mr
INNER JOIN `users` req ON mr.user_id = req.id
LEFT JOIN `users` rev ON mr.reviewed_by = rev.id
ORDER BY mr.created_at DESC;


-- 2e. Member Payments LEFT JOIN Payment Proofs: Payments with/without proof
SELECT u.full_name, u.student_id,
       mp.year, mp.month, mp.status AS payment_status,
       COUNT(pp.id) AS proof_count,
       GROUP_CONCAT(pp.status SEPARATOR ', ') AS proof_statuses
FROM `member_payments` mp
INNER JOIN `users` u ON mp.user_id = u.id
LEFT JOIN `payment_proofs` pp ON mp.id = pp.member_payment_id
WHERE mp.year = 2026
GROUP BY mp.id, u.full_name, u.student_id, mp.year, mp.month, mp.status
ORDER BY mp.month, u.full_name;


-- 2f. Payment Proofs LEFT JOIN Reviewer: Proofs with optional reviewer
SELECT pp.proof_type, pp.proof_value, pp.status,
       submitter.full_name AS submitted_by,
       reviewer.full_name AS reviewed_by,
       pp.reviewed_at, pp.rejection_note
FROM `payment_proofs` pp
INNER JOIN `users` submitter ON pp.user_id = submitter.id
LEFT JOIN `users` reviewer ON pp.reviewed_by = reviewer.id
ORDER BY pp.created_at DESC;


-- ============================================================================
-- 3. MULTI-TABLE JOINS (3+ tables)
-- ============================================================================

-- 3a. Full meal request pipeline: Request + Requester + Payment + Reviewer
SELECT mr.id AS request_id,
       mr.date, mr.meal_type, mr.reason,
       mr.status AS request_status,
       req.full_name AS requester_name,
       req.student_id, req.department,
       p.amount, p.payment_method, p.reference_no,
       rev.full_name AS reviewer_name,
       mr.reviewed_at, mr.rejection_note
FROM `meal_requests` mr
INNER JOIN `users` req ON mr.user_id = req.id
LEFT JOIN `payments` p ON mr.payment_id = p.id
LEFT JOIN `users` rev ON mr.reviewed_by = rev.id
ORDER BY mr.created_at DESC;


-- 3b. Payment proof pipeline: Proof + MemberPayment + Submitter + Reviewer
SELECT u.full_name AS student_name, u.student_id,
       mp.year, mp.month, mp.amount_due, mp.amount_paid,
       pp.proof_type, pp.proof_value, pp.status AS proof_status,
       rev.full_name AS reviewed_by
FROM `payment_proofs` pp
INNER JOIN `member_payments` mp ON pp.member_payment_id = mp.id
INNER JOIN `users` u ON pp.user_id = u.id
LEFT JOIN `users` rev ON pp.reviewed_by = rev.id
ORDER BY mp.year DESC, mp.month DESC;


-- 3c. Complete daily view: Menu + Items + Student Meals for a date
SELECT dm.meal_type,
       GROUP_CONCAT(DISTINCT mi.food_name ORDER BY mi.food_name SEPARATOR ', ') AS menu_items,
       COUNT(DISTINCT sm.id) AS enrolled_students,
       SUM(CASE WHEN sm.status = 'ACTIVE' THEN 1 ELSE 0 END) AS active_meals,
       SUM(CASE WHEN sm.status = 'CANCELLED' THEN 1 ELSE 0 END) AS cancelled_meals
FROM `daily_menus` dm
LEFT JOIN `menu_items` mi ON dm.id = mi.menu_id
LEFT JOIN `student_meals` sm ON dm.date = sm.date AND dm.meal_type = sm.meal_type
WHERE dm.date = '2026-06-24'
GROUP BY dm.meal_type
ORDER BY FIELD(dm.meal_type, 'BREAKFAST', 'LUNCH', 'DINNER');


-- 3d. Meal schedule + daily menu + items: Full schedule view
SELECT ms.meal_type, ms.start_time, ms.end_time, ms.cancel_deadline,
       dm.date, dm.is_cancelled,
       GROUP_CONCAT(mi.food_name SEPARATOR ', ') AS items
FROM `meal_schedules` ms
LEFT JOIN `daily_menus` dm ON ms.meal_type = dm.meal_type AND dm.date = '2026-06-24'
LEFT JOIN `menu_items` mi ON dm.id = mi.menu_id
WHERE ms.is_active = 1
GROUP BY ms.meal_type, ms.start_time, ms.end_time, ms.cancel_deadline, dm.date, dm.is_cancelled
ORDER BY ms.start_time;


-- ============================================================================
-- 4. SELF-JOINS
-- ============================================================================

-- 4a. Meal schedules: Created by + Updated by (same users table, different roles)
SELECT ms.meal_type, ms.start_time, ms.end_time,
       creator.full_name AS created_by_name, creator.role AS creator_role,
       updater.full_name AS updated_by_name
FROM `meal_schedules` ms
INNER JOIN `users` creator ON ms.created_by = creator.id
LEFT JOIN `users` updater ON ms.updated_by = updater.id;


-- 4b. Expenses: Created by + Updated by
SELECT e.name, e.amount, e.expense_date,
       creator.full_name AS created_by,
       updater.full_name AS last_updated_by
FROM `expenses` e
INNER JOIN `users` creator ON e.created_by = creator.id
LEFT JOIN `users` updater ON e.updated_by = updater.id;


-- ============================================================================
-- 5. SUBQUERY JOINS
-- ============================================================================

-- 5a. Customers who have NOT enrolled for any meal today
SELECT u.full_name, u.student_id, u.department
FROM `users` u
WHERE u.role = 'CUSTOMER'
  AND u.status = 'ACTIVE'
  AND u.id NOT IN (
    SELECT sm.user_id FROM `student_meals` sm
    WHERE sm.date = CURDATE() AND sm.status = 'ACTIVE'
  );


-- 5b. Users with the most meal cancellations (top 5)
SELECT u.full_name, u.student_id, cancel_counts.cancellation_count
FROM `users` u
INNER JOIN (
  SELECT user_id, COUNT(*) AS cancellation_count
  FROM `student_meals`
  WHERE status = 'CANCELLED'
  GROUP BY user_id
  ORDER BY cancellation_count DESC
  LIMIT 5
) cancel_counts ON u.id = cancel_counts.user_id
ORDER BY cancel_counts.cancellation_count DESC;


-- 5c. Months where expenses exceeded earnings
SELECT exp_month.m_year, exp_month.m_month,
       exp_month.total_expenses, earn_month.total_earnings,
       (COALESCE(earn_month.total_earnings, 0) - exp_month.total_expenses) AS net_balance
FROM (
  SELECT YEAR(expense_date) AS m_year, MONTH(expense_date) AS m_month,
         SUM(amount) AS total_expenses
  FROM `expenses`
  GROUP BY YEAR(expense_date), MONTH(expense_date)
) exp_month
LEFT JOIN (
  SELECT YEAR(earning_date) AS m_year, MONTH(earning_date) AS m_month,
         SUM(amount) AS total_earnings
  FROM `earnings`
  GROUP BY YEAR(earning_date), MONTH(earning_date)
) earn_month ON exp_month.m_year = earn_month.m_year AND exp_month.m_month = earn_month.m_month
ORDER BY exp_month.m_year, exp_month.m_month;
