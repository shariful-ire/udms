-- ============================================================================
-- UDMS — CRUD Examples for Every Table
-- ============================================================================
-- Demonstrates CREATE, READ, UPDATE, DELETE operations per table.
-- Uses sample data UUIDs from sample_data.sql.
-- ============================================================================

USE `udms`;


-- ████████████████████████████████████████████████████████████████████████████
-- TABLE: users
-- ████████████████████████████████████████████████████████████████████████████

-- CREATE: Register a new student
INSERT INTO `users` (`id`, `student_id`, `username`, `full_name`, `email`, `password_hash`, `role`, `department`, `batch`, `hall_name`, `status`, `email_verified`, `failed_attempts`)
VALUES (UUID(), 'EdTE-2003-010', 'sadia_r', 'Sadia Rahman', 'sadia@university.edu',
        '$argon2id$v=19$m=65536,t=2,p=2$placeholder', 'NON_CUSTOMER', 'EdTE', '2022', 'UFTB Girls Hall-2', 'INACTIVE', 0, 0);

-- READ: Get all active customers
SELECT id, student_id, full_name, email, department, hall_name
FROM `users`
WHERE role = 'CUSTOMER' AND status = 'ACTIVE';

-- READ: Search user by student ID
SELECT * FROM `users` WHERE student_id = 'IRE-2001-001';

-- READ: List users with pagination
SELECT id, student_id, full_name, role, status
FROM `users`
ORDER BY created_at DESC
LIMIT 20 OFFSET 0;

-- UPDATE: Activate a user after email verification
UPDATE `users`
SET status = 'ACTIVE', email_verified = 1, updated_at = NOW()
WHERE id = '55555555-5555-5555-5555-555555555555';

-- UPDATE: Assign a user as Dining Manager
UPDATE `users`
SET role = 'DINING_MANAGER', updated_at = NOW()
WHERE id = '66666666-6666-6666-6666-666666666666';

-- UPDATE: Suspend a user
UPDATE `users`
SET status = 'SUSPENDED', updated_at = NOW()
WHERE id = '66666666-6666-6666-6666-666666666666';

-- UPDATE: Record failed login attempt
UPDATE `users`
SET failed_attempts = failed_attempts + 1,
    locked_until = CASE WHEN failed_attempts + 1 >= 5 THEN DATE_ADD(NOW(), INTERVAL 15 MINUTE) ELSE locked_until END
WHERE id = '33333333-3333-3333-3333-333333333333';

-- DELETE: Remove a user (cascades to refresh_tokens, student_meals, member_payments)
DELETE FROM `users` WHERE id = 'some-uuid-to-delete';


-- ████████████████████████████████████████████████████████████████████████████
-- TABLE: refresh_tokens
-- ████████████████████████████████████████████████████████████████████████████

-- CREATE: Store a new refresh token
INSERT INTO `refresh_tokens` (`id`, `user_id`, `token_hash`, `expires_at`)
VALUES (UUID(), '33333333-3333-3333-3333-333333333333',
        SHA2('sample-jwt-refresh-token-string', 256),
        DATE_ADD(NOW(), INTERVAL 7 DAY));

-- READ: Check if a token is valid and not expired
SELECT rt.*, u.username, u.role
FROM `refresh_tokens` rt
JOIN `users` u ON rt.user_id = u.id
WHERE rt.token_hash = SHA2('sample-jwt-refresh-token-string', 256)
  AND rt.expires_at > NOW();

-- UPDATE: (Refresh tokens are not updated — old ones are deleted, new ones created)

-- DELETE: Invalidate a specific token (logout)
DELETE FROM `refresh_tokens`
WHERE token_hash = SHA2('sample-jwt-refresh-token-string', 256);

-- DELETE: Purge all expired tokens
DELETE FROM `refresh_tokens` WHERE expires_at < NOW();


-- ████████████████████████████████████████████████████████████████████████████
-- TABLE: meal_schedules
-- ████████████████████████████████████████████████████████████████████████████

-- CREATE: (Rarely done — 3 rows exist: BREAKFAST, LUNCH, DINNER)
INSERT INTO `meal_schedules` (`id`, `meal_type`, `start_time`, `end_time`, `cancel_deadline`, `is_active`, `created_by`)
VALUES (UUID(), 'BREAKFAST', '07:00:00', '09:00:00', '06:30:00', 1, '22222222-2222-2222-2222-222222222222');

-- READ: Get all active meal schedules
SELECT meal_type, start_time, end_time, cancel_deadline, is_active
FROM `meal_schedules`
WHERE is_active = 1
ORDER BY start_time;

-- UPDATE: Change lunch timing
UPDATE `meal_schedules`
SET start_time = '12:30:00', end_time = '14:30:00', cancel_deadline = '12:00:00',
    updated_by = '22222222-2222-2222-2222-222222222222'
WHERE meal_type = 'LUNCH';

-- UPDATE: Deactivate a meal type
UPDATE `meal_schedules`
SET is_active = 0, updated_by = '22222222-2222-2222-2222-222222222222'
WHERE meal_type = 'BREAKFAST';

-- DELETE: (Generally not deleted — deactivated instead)


-- ████████████████████████████████████████████████████████████████████████████
-- TABLE: daily_menus
-- ████████████████████████████████████████████████████████████████████████████

-- CREATE: Create a menu for a new date
INSERT INTO `daily_menus` (`id`, `date`, `meal_type`, `is_cancelled`, `created_by`)
VALUES (UUID(), '2026-06-26', 'LUNCH', 0, '22222222-2222-2222-2222-222222222222');

-- READ: Get all menus for a specific date
SELECT dm.id, dm.date, dm.meal_type, dm.is_cancelled,
       GROUP_CONCAT(mi.food_name ORDER BY mi.food_name SEPARATOR ', ') AS items
FROM `daily_menus` dm
LEFT JOIN `menu_items` mi ON dm.id = mi.menu_id
WHERE dm.date = '2026-06-24'
GROUP BY dm.id, dm.date, dm.meal_type, dm.is_cancelled;

-- READ: Get menus for a date range
SELECT * FROM `daily_menus`
WHERE date BETWEEN '2026-06-23' AND '2026-06-25'
ORDER BY date, FIELD(meal_type, 'BREAKFAST', 'LUNCH', 'DINNER');

-- UPDATE: Cancel a menu
UPDATE `daily_menus`
SET is_cancelled = 1, updated_by = '22222222-2222-2222-2222-222222222222'
WHERE id = 'dm-00009-0000-0000-000000000009';

-- DELETE: Remove a menu (cascades to menu_items)
DELETE FROM `daily_menus` WHERE id = 'dm-00009-0000-0000-000000000009';


-- ████████████████████████████████████████████████████████████████████████████
-- TABLE: menu_items
-- ████████████████████████████████████████████████████████████████████████████

-- CREATE: Add a food item to an existing menu
INSERT INTO `menu_items` (`id`, `menu_id`, `food_name`, `quantity`, `notes`)
VALUES (UUID(), 'dm-00005-0000-0000-000000000005', 'Water', '1 bottle', 'Mineral water');

-- READ: Get all items for a specific menu
SELECT food_name, quantity, notes
FROM `menu_items`
WHERE menu_id = 'dm-00002-0000-0000-000000000002'
ORDER BY food_name;

-- UPDATE: Change a menu item quantity
UPDATE `menu_items`
SET food_name = 'Chicken Curry (Spicy)', quantity = '3 pieces'
WHERE id = 'mi-00015-0000-0000-000000000015';

-- DELETE: Remove a food item from a menu
DELETE FROM `menu_items` WHERE id = 'mi-00003-0000-0000-000000000003';


-- ████████████████████████████████████████████████████████████████████████████
-- TABLE: student_meals
-- ████████████████████████████████████████████████████████████████████████████

-- CREATE: Customer enrolls for a meal
INSERT INTO `student_meals` (`id`, `user_id`, `date`, `meal_type`, `status`)
VALUES (UUID(), '33333333-3333-3333-3333-333333333333', '2026-06-26', 'LUNCH', 'ACTIVE');

-- READ: Get today's meal status for a customer
SELECT meal_type, status, cancelled_at
FROM `student_meals`
WHERE user_id = '33333333-3333-3333-3333-333333333333'
  AND date = CURDATE()
ORDER BY FIELD(meal_type, 'BREAKFAST', 'LUNCH', 'DINNER');

-- READ: Get meal history for a customer (paginated)
SELECT date, meal_type, status, created_at
FROM `student_meals`
WHERE user_id = '33333333-3333-3333-3333-333333333333'
ORDER BY date DESC, FIELD(meal_type, 'BREAKFAST', 'LUNCH', 'DINNER')
LIMIT 20 OFFSET 0;

-- UPDATE: Cancel a meal (before deadline)
UPDATE `student_meals`
SET status = 'CANCELLED', cancelled_at = NOW()
WHERE id = 'sm-00005-0000-0000-000000000005'
  AND status = 'ACTIVE';

-- DELETE: (Meals are cancelled, not deleted — preserves history)


-- ████████████████████████████████████████████████████████████████████████████
-- TABLE: expenses
-- ████████████████████████████████████████████████████████████████████████████

-- CREATE: Log a new expense
INSERT INTO `expenses` (`id`, `name`, `category`, `amount`, `description`, `expense_date`, `created_by`)
VALUES (UUID(), 'Spices and Condiments', 'FOOD_PURCHASE', 2500.00,
        'Monthly spice purchase', '2026-06-22', '22222222-2222-2222-2222-222222222222');

-- READ: Get expenses filtered by category and date
SELECT name, category, amount, expense_date
FROM `expenses`
WHERE category = 'FOOD_PURCHASE'
  AND expense_date BETWEEN '2026-06-01' AND '2026-06-30'
ORDER BY expense_date;

-- READ: Get all expenses with creator info
SELECT e.name, e.category, e.amount, e.expense_date, u.full_name AS created_by_name
FROM `expenses` e
JOIN `users` u ON e.created_by = u.id
ORDER BY e.expense_date DESC;

-- UPDATE: Correct an expense amount
UPDATE `expenses`
SET amount = 16000.00, description = 'Rice and grains for June (corrected)',
    updated_by = '22222222-2222-2222-2222-222222222222'
WHERE id = 'ex-00001-0000-0000-000000000001';

-- DELETE: Remove an expense
DELETE FROM `expenses` WHERE id = 'ex-00010-0000-0000-000000000010';


-- ████████████████████████████████████████████████████████████████████████████
-- TABLE: earnings
-- ████████████████████████████████████████████████████████████████████████████

-- CREATE: Record new income
INSERT INTO `earnings` (`id`, `description`, `category`, `amount`, `earning_date`, `notes`, `created_by`)
VALUES (UUID(), 'Late Payment Collection', 'MEAL_PAYMENT', 7000.00,
        '2026-06-22', 'Collected overdue May payments', '22222222-2222-2222-2222-222222222222');

-- READ: Get all earnings for a month
SELECT description, category, amount, earning_date
FROM `earnings`
WHERE earning_date BETWEEN '2026-06-01' AND '2026-06-30'
ORDER BY earning_date;

-- UPDATE: Correct an earning record
UPDATE `earnings`
SET amount = 46000.00, notes = 'Collected from 31 customers (corrected)'
WHERE id = 'ea-00001-0000-0000-000000000001';

-- DELETE: Remove an earning record
DELETE FROM `earnings` WHERE id = 'ea-00005-0000-0000-000000000005';


-- ████████████████████████████████████████████████████████████████████████████
-- TABLE: payments
-- ████████████████████████████████████████████████████████████████████████████

-- CREATE: Record a new payment
INSERT INTO `payments` (`id`, `user_id`, `amount`, `payment_method`, `reference_no`, `status`, `note`)
VALUES (UUID(), '55555555-5555-5555-5555-555555555555', 80.00,
        'MOBILE_BANKING', 'TXN999888', 'COMPLETED', 'bKash payment for dinner request');

-- READ: Get all payments for a user
SELECT amount, payment_method, reference_no, status, created_at
FROM `payments`
WHERE user_id = '55555555-5555-5555-5555-555555555555'
ORDER BY created_at DESC;

-- READ: Get pending payments
SELECT p.*, u.full_name
FROM `payments` p
JOIN `users` u ON p.user_id = u.id
WHERE p.status = 'PENDING';

-- UPDATE: Mark payment as completed
UPDATE `payments`
SET status = 'COMPLETED'
WHERE id = 'py-00003-0000-0000-000000000003';

-- UPDATE: Refund a payment
UPDATE `payments`
SET status = 'REFUNDED', note = 'Refunded due to cancelled request'
WHERE id = 'py-00004-0000-0000-000000000004';

-- DELETE: (Payments are not deleted — status is changed)


-- ████████████████████████████████████████████████████████████████████████████
-- TABLE: meal_requests
-- ████████████████████████████████████████████████████████████████████████████

-- CREATE: Non-customer submits a meal request
INSERT INTO `meal_requests` (`id`, `user_id`, `date`, `meal_type`, `reason`, `status`)
VALUES (UUID(), '66666666-6666-6666-6666-666666666666', '2026-06-27', 'DINNER',
        'Evening event at the hall', 'PENDING_PAYMENT');

-- READ: Get all pending requests for manager review
SELECT mr.id, mr.date, mr.meal_type, mr.reason, mr.status,
       u.full_name AS requester, u.student_id
FROM `meal_requests` mr
JOIN `users` u ON mr.user_id = u.id
WHERE mr.status IN ('PENDING_PAYMENT', 'PENDING_APPROVAL')
ORDER BY mr.date, mr.meal_type;

-- READ: Get a user's request history
SELECT date, meal_type, status, rejection_note, created_at
FROM `meal_requests`
WHERE user_id = '55555555-5555-5555-5555-555555555555'
ORDER BY created_at DESC;

-- UPDATE: Link payment and advance to pending approval
UPDATE `meal_requests`
SET status = 'PENDING_APPROVAL', payment_id = 'py-00003-0000-0000-000000000003'
WHERE id = 'mr-00003-0000-0000-000000000003';

-- UPDATE: Approve a request
UPDATE `meal_requests`
SET status = 'APPROVED',
    reviewed_by = '22222222-2222-2222-2222-222222222222',
    reviewed_at = NOW()
WHERE id = 'mr-00002-0000-0000-000000000002';

-- UPDATE: Reject a request with note
UPDATE `meal_requests`
SET status = 'REJECTED',
    reviewed_by = '22222222-2222-2222-2222-222222222222',
    reviewed_at = NOW(),
    rejection_note = 'Date conflict with scheduled maintenance'
WHERE id = 'mr-00003-0000-0000-000000000003';

-- DELETE: Cancel own request (non-customer)
UPDATE `meal_requests`
SET status = 'CANCELLED'
WHERE id = 'mr-00005-0000-0000-000000000005'
  AND user_id = '55555555-5555-5555-5555-555555555555';


-- ████████████████████████████████████████████████████████████████████████████
-- TABLE: member_payments
-- ████████████████████████████████████████████████████████████████████████████

-- CREATE: Initialize monthly payment records for all active customers
INSERT INTO `member_payments` (`id`, `user_id`, `year`, `month`, `amount_due`, `amount_paid`, `status`)
SELECT UUID(), u.id, 2026, 7, 3500.00, 0.00, 'PENDING'
FROM `users` u
WHERE u.role = 'CUSTOMER' AND u.status = 'ACTIVE';

-- READ: Get payment status for a specific month
SELECT mp.*, u.full_name, u.student_id
FROM `member_payments` mp
JOIN `users` u ON mp.user_id = u.id
WHERE mp.year = 2026 AND mp.month = 6
ORDER BY u.full_name;

-- READ: Payment summary counts
SELECT
  status,
  COUNT(*) AS count,
  SUM(amount_due) AS total_due,
  SUM(amount_paid) AS total_paid
FROM `member_payments`
WHERE year = 2026 AND month = 6
GROUP BY status;

-- UPDATE: Mark a payment as paid
UPDATE `member_payments`
SET status = 'PAID', amount_paid = amount_due
WHERE id = 'mp-00002-0000-0000-000000000002';

-- UPDATE: Record partial payment
UPDATE `member_payments`
SET amount_paid = 3000.00
WHERE id = 'mp-00004-0000-0000-000000000004';

-- DELETE: (Member payments are not deleted — status is managed)


-- ████████████████████████████████████████████████████████████████████████████
-- TABLE: payment_proofs
-- ████████████████████████████████████████████████████████████████████████████

-- CREATE: Customer submits payment proof
INSERT INTO `payment_proofs` (`id`, `member_payment_id`, `user_id`, `proof_type`, `proof_value`, `status`)
VALUES (UUID(), 'mp-00004-0000-0000-000000000004', '44444444-4444-4444-4444-444444444444',
        'TRANSACTION_ID', 'TXN-BKASH-20260622-5678', 'SUBMITTED');

-- READ: Get all proofs for a member payment
SELECT pp.proof_type, pp.proof_value, pp.status, pp.rejection_note,
       u.full_name AS submitted_by, r.full_name AS reviewed_by_name
FROM `payment_proofs` pp
JOIN `users` u ON pp.user_id = u.id
LEFT JOIN `users` r ON pp.reviewed_by = r.id
WHERE pp.member_payment_id = 'mp-00002-0000-0000-000000000002';

-- READ: Get all submitted (pending review) proofs
SELECT pp.*, u.full_name, u.student_id
FROM `payment_proofs` pp
JOIN `users` u ON pp.user_id = u.id
WHERE pp.status = 'SUBMITTED'
ORDER BY pp.created_at;

-- UPDATE: Approve a proof (also mark the parent member_payment as PAID)
UPDATE `payment_proofs`
SET status = 'APPROVED',
    reviewed_by = '22222222-2222-2222-2222-222222222222',
    reviewed_at = NOW()
WHERE id = 'pp-00002-0000-0000-000000000002';

-- UPDATE: Reject a proof with note
UPDATE `payment_proofs`
SET status = 'REJECTED',
    reviewed_by = '22222222-2222-2222-2222-222222222222',
    reviewed_at = NOW(),
    rejection_note = 'Screenshot is blurry, please resubmit'
WHERE id = 'pp-00002-0000-0000-000000000002';

-- DELETE: (Proofs are not deleted — status is managed)


-- ████████████████████████████████████████████████████████████████████████████
-- TABLE: audit_logs
-- ████████████████████████████████████████████████████████████████████████████

-- CREATE: Log an action
INSERT INTO `audit_logs` (`user_id`, `action`, `entity_type`, `entity_id`, `new_value`, `ip_address`, `user_agent`)
VALUES ('22222222-2222-2222-2222-222222222222', 'EXPENSE_CREATED', 'Expense', UUID(),
        '{"name": "Spices Purchase", "amount": 2500}', '192.168.1.10', 'Mozilla/5.0');

-- READ: Get recent audit logs with user info
SELECT al.action, al.entity_type, al.created_at,
       u.full_name AS actor, al.ip_address
FROM `audit_logs` al
LEFT JOIN `users` u ON al.user_id = u.id
ORDER BY al.created_at DESC
LIMIT 50;

-- READ: Get logs for a specific entity
SELECT action, old_value, new_value, created_at
FROM `audit_logs`
WHERE entity_type = 'User' AND entity_id = '33333333-3333-3333-3333-333333333333'
ORDER BY created_at;

-- READ: Get logs filtered by action type
SELECT * FROM `audit_logs`
WHERE action LIKE 'MEAL_%'
ORDER BY created_at DESC;

-- UPDATE: (Audit logs are immutable — never updated)

-- DELETE: (Audit logs are immutable — never deleted)


-- ████████████████████████████████████████████████████████████████████████████
-- TABLE: system_settings
-- ████████████████████████████████████████████████████████████████████████████

-- CREATE: Add a new setting
INSERT INTO `system_settings` (`key_name`, `value`, `description`, `updated_by`)
VALUES ('dining_hall_capacity', '200', 'Maximum seating capacity', '11111111-1111-1111-1111-111111111111');

-- READ: Get a specific setting
SELECT value FROM `system_settings` WHERE key_name = 'meal_price_non_customer';

-- READ: Get all settings
SELECT key_name, value, description, updated_at
FROM `system_settings`
ORDER BY key_name;

-- UPDATE: Change meal price
UPDATE `system_settings`
SET value = '100.00', updated_by = '11111111-1111-1111-1111-111111111111'
WHERE key_name = 'meal_price_non_customer';

-- DELETE: Remove a setting
DELETE FROM `system_settings` WHERE key_name = 'dining_hall_capacity';
