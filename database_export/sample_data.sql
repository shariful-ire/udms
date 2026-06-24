-- ============================================================================
-- UDMS — Sample Data (INSERT Statements)
-- ============================================================================
-- Run AFTER udms_database.sql
-- Uses fixed UUIDs so foreign key references are consistent
-- Password hashes below are Argon2id hashes of the listed passwords
-- ============================================================================

USE `udms`;

SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================================
-- 1. USERS (6 accounts)
-- ============================================================================
-- Passwords (for reference — hashes are bcrypt stand-ins for XAMPP demo):
--   Provost:      Admin@1234!
--   Manager:      Manager@1234!
--   Customers:    Student@1234!
--   Non-Customers: Student@1234!
-- Note: In the real app, Argon2id hashes are used. Below we use a placeholder
-- hash since Argon2id cannot be generated in plain SQL.

INSERT INTO `users` (`id`, `student_id`, `username`, `full_name`, `email`, `password_hash`, `role`, `department`, `batch`, `hall_name`, `phone`, `status`, `email_verified`, `failed_attempts`) VALUES
-- Provost (Hall Administrator)
('11111111-1111-1111-1111-111111111111', 'PROVOST-001', 'provost', 'Prof. Dr. Rahman Ali', 'provost@university.edu',
 '$argon2id$v=19$m=65536,t=2,p=2$placeholder_hash_provost', 'PROVOST', 'Administration', 'N/A', 'UFTB Boys Hall', '01711000001', 'ACTIVE', 1, 0),

-- Dining Manager
('22222222-2222-2222-2222-222222222222', 'STAFF-001', 'diningmgr', 'Karim Hossain', 'manager@university.edu',
 '$argon2id$v=19$m=65536,t=2,p=2$placeholder_hash_manager', 'DINING_MANAGER', 'IRE', 'N/A', 'UFTB Boys Hall', '01711000002', 'ACTIVE', 1, 0),

-- Customer 1 (enrolled dining student)
('33333333-3333-3333-3333-333333333333', 'IRE-2001-001', 'arif_hasan', 'Arif Hasan', 'arif@university.edu',
 '$argon2id$v=19$m=65536,t=2,p=2$placeholder_hash_student1', 'CUSTOMER', 'IRE', '2020', 'UFTB Boys Hall', '01711000003', 'ACTIVE', 1, 0),

-- Customer 2
('44444444-4444-4444-4444-444444444444', 'DSE-2002-002', 'fatima_khan', 'Fatima Khan', 'fatima@university.edu',
 '$argon2id$v=19$m=65536,t=2,p=2$placeholder_hash_student2', 'CUSTOMER', 'DSE', '2021', 'UFTB Girls Hall-1', '01711000004', 'ACTIVE', 1, 0),

-- Non-Customer 1 (not enrolled, can submit meal requests)
('55555555-5555-5555-5555-555555555555', 'CySE-2001-003', 'nadia_islam', 'Nadia Islam', 'nadia@university.edu',
 '$argon2id$v=19$m=65536,t=2,p=2$placeholder_hash_student3', 'NON_CUSTOMER', 'CySE', '2021', 'UFTB Girls Hall-1', '01711000005', 'ACTIVE', 1, 0),

-- Non-Customer 2
('66666666-6666-6666-6666-666666666666', 'SE-2003-004', 'rubel_ahmed', 'Rubel Ahmed', 'rubel@university.edu',
 '$argon2id$v=19$m=65536,t=2,p=2$placeholder_hash_student4', 'NON_CUSTOMER', 'SE', '2022', 'UFTB Boys Hall', '01711000006', 'ACTIVE', 1, 0);


-- ============================================================================
-- 2. MEAL SCHEDULES (3 rows — one per meal type)
-- ============================================================================
INSERT INTO `meal_schedules` (`id`, `meal_type`, `start_time`, `end_time`, `cancel_deadline`, `is_active`, `created_by`) VALUES
('ms-00001-0000-0000-000000000001', 'BREAKFAST', '07:00:00', '09:00:00', '06:30:00', 1, '22222222-2222-2222-2222-222222222222'),
('ms-00002-0000-0000-000000000002', 'LUNCH',     '12:00:00', '14:00:00', '11:30:00', 1, '22222222-2222-2222-2222-222222222222'),
('ms-00003-0000-0000-000000000003', 'DINNER',    '19:00:00', '21:00:00', '18:30:00', 1, '22222222-2222-2222-2222-222222222222');


-- ============================================================================
-- 3. DAILY MENUS (9 menus — 3 days x 3 meal types)
-- ============================================================================
INSERT INTO `daily_menus` (`id`, `date`, `meal_type`, `is_cancelled`, `created_by`) VALUES
('dm-00001-0000-0000-000000000001', '2026-06-23', 'BREAKFAST', 0, '22222222-2222-2222-2222-222222222222'),
('dm-00002-0000-0000-000000000002', '2026-06-23', 'LUNCH',     0, '22222222-2222-2222-2222-222222222222'),
('dm-00003-0000-0000-000000000003', '2026-06-23', 'DINNER',    0, '22222222-2222-2222-2222-222222222222'),
('dm-00004-0000-0000-000000000004', '2026-06-24', 'BREAKFAST', 0, '22222222-2222-2222-2222-222222222222'),
('dm-00005-0000-0000-000000000005', '2026-06-24', 'LUNCH',     0, '22222222-2222-2222-2222-222222222222'),
('dm-00006-0000-0000-000000000006', '2026-06-24', 'DINNER',    0, '22222222-2222-2222-2222-222222222222'),
('dm-00007-0000-0000-000000000007', '2026-06-25', 'BREAKFAST', 0, '22222222-2222-2222-2222-222222222222'),
('dm-00008-0000-0000-000000000008', '2026-06-25', 'LUNCH',     0, '22222222-2222-2222-2222-222222222222'),
('dm-00009-0000-0000-000000000009', '2026-06-25', 'DINNER',    1, '22222222-2222-2222-2222-222222222222');


-- ============================================================================
-- 4. MENU ITEMS (food items for each daily menu)
-- ============================================================================
INSERT INTO `menu_items` (`id`, `menu_id`, `food_name`, `quantity`, `notes`) VALUES
-- Jun 23 Breakfast
('mi-00001-0000-0000-000000000001', 'dm-00001-0000-0000-000000000001', 'Paratha',  '2 pieces', NULL),
('mi-00002-0000-0000-000000000002', 'dm-00001-0000-0000-000000000001', 'Egg Fry',  '1 piece',  NULL),
('mi-00003-0000-0000-000000000003', 'dm-00001-0000-0000-000000000001', 'Tea',      '1 cup',    NULL),
-- Jun 23 Lunch
('mi-00004-0000-0000-000000000004', 'dm-00002-0000-0000-000000000002', 'Rice',         '1 plate',  NULL),
('mi-00005-0000-0000-000000000005', 'dm-00002-0000-0000-000000000002', 'Dal',          '1 bowl',   NULL),
('mi-00006-0000-0000-000000000006', 'dm-00002-0000-0000-000000000002', 'Fish Curry',   '2 pieces',  NULL),
('mi-00007-0000-0000-000000000007', 'dm-00002-0000-0000-000000000002', 'Vegetable',    '1 bowl',   NULL),
-- Jun 23 Dinner
('mi-00008-0000-0000-000000000008', 'dm-00003-0000-0000-000000000003', 'Rice',           '1 plate', NULL),
('mi-00009-0000-0000-000000000009', 'dm-00003-0000-0000-000000000003', 'Chicken Roast',  '1 piece', NULL),
('mi-00010-0000-0000-000000000010', 'dm-00003-0000-0000-000000000003', 'Mixed Vegetable','1 bowl',  NULL),
-- Jun 24 Breakfast
('mi-00011-0000-0000-000000000011', 'dm-00004-0000-0000-000000000004', 'Puri',    '3 pieces', NULL),
('mi-00012-0000-0000-000000000012', 'dm-00004-0000-0000-000000000004', 'Halwa',   '1 bowl',   NULL),
('mi-00013-0000-0000-000000000013', 'dm-00004-0000-0000-000000000004', 'Lassi',   '1 glass',  NULL),
-- Jun 24 Lunch
('mi-00014-0000-0000-000000000014', 'dm-00005-0000-0000-000000000005', 'Rice',          '1 plate', NULL),
('mi-00015-0000-0000-000000000015', 'dm-00005-0000-0000-000000000005', 'Chicken Curry', '2 pieces', NULL),
('mi-00016-0000-0000-000000000016', 'dm-00005-0000-0000-000000000005', 'Salad',         '1 bowl',  NULL),
-- Jun 24 Dinner
('mi-00017-0000-0000-000000000017', 'dm-00006-0000-0000-000000000006', 'Rice',       '1 plate', NULL),
('mi-00018-0000-0000-000000000018', 'dm-00006-0000-0000-000000000006', 'Beef Curry', '150g',    NULL),
('mi-00019-0000-0000-000000000019', 'dm-00006-0000-0000-000000000006', 'Dal',        '1 bowl',  NULL),
-- Jun 25 Breakfast
('mi-00020-0000-0000-000000000020', 'dm-00007-0000-0000-000000000007', 'Paratha', '2 pieces', NULL),
('mi-00021-0000-0000-000000000021', 'dm-00007-0000-0000-000000000007', 'Egg Fry', '1 piece',  NULL),
-- Jun 25 Lunch
('mi-00022-0000-0000-000000000022', 'dm-00008-0000-0000-000000000008', 'Rice',       '1 plate',  NULL),
('mi-00023-0000-0000-000000000023', 'dm-00008-0000-0000-000000000008', 'Beef Bhuna', '150g',     NULL),
('mi-00024-0000-0000-000000000024', 'dm-00008-0000-0000-000000000008', 'Vegetable',  '1 bowl',   NULL);


-- ============================================================================
-- 5. STUDENT MEALS (meal enrollments for customers)
-- ============================================================================
INSERT INTO `student_meals` (`id`, `user_id`, `date`, `meal_type`, `status`, `cancelled_at`) VALUES
-- Arif Hasan (Customer 1) — 3 days of meals
('sm-00001-0000-0000-000000000001', '33333333-3333-3333-3333-333333333333', '2026-06-23', 'BREAKFAST', 'ACTIVE',    NULL),
('sm-00002-0000-0000-000000000002', '33333333-3333-3333-3333-333333333333', '2026-06-23', 'LUNCH',     'ACTIVE',    NULL),
('sm-00003-0000-0000-000000000003', '33333333-3333-3333-3333-333333333333', '2026-06-23', 'DINNER',    'CANCELLED', '2026-06-23 17:00:00'),
('sm-00004-0000-0000-000000000004', '33333333-3333-3333-3333-333333333333', '2026-06-24', 'BREAKFAST', 'ACTIVE',    NULL),
('sm-00005-0000-0000-000000000005', '33333333-3333-3333-3333-333333333333', '2026-06-24', 'LUNCH',     'ACTIVE',    NULL),
('sm-00006-0000-0000-000000000006', '33333333-3333-3333-3333-333333333333', '2026-06-24', 'DINNER',    'ACTIVE',    NULL),
('sm-00007-0000-0000-000000000007', '33333333-3333-3333-3333-333333333333', '2026-06-25', 'BREAKFAST', 'ACTIVE',    NULL),
-- Fatima Khan (Customer 2) — 3 days of meals
('sm-00008-0000-0000-000000000008', '44444444-4444-4444-4444-444444444444', '2026-06-23', 'BREAKFAST', 'ACTIVE',    NULL),
('sm-00009-0000-0000-000000000009', '44444444-4444-4444-4444-444444444444', '2026-06-23', 'LUNCH',     'ACTIVE',    NULL),
('sm-00010-0000-0000-000000000010', '44444444-4444-4444-4444-444444444444', '2026-06-23', 'DINNER',    'ACTIVE',    NULL),
('sm-00011-0000-0000-000000000011', '44444444-4444-4444-4444-444444444444', '2026-06-24', 'BREAKFAST', 'CANCELLED', '2026-06-24 06:00:00'),
('sm-00012-0000-0000-000000000012', '44444444-4444-4444-4444-444444444444', '2026-06-24', 'LUNCH',     'ACTIVE',    NULL),
('sm-00013-0000-0000-000000000013', '44444444-4444-4444-4444-444444444444', '2026-06-24', 'DINNER',    'ACTIVE',    NULL),
('sm-00014-0000-0000-000000000014', '44444444-4444-4444-4444-444444444444', '2026-06-25', 'BREAKFAST', 'ACTIVE',    NULL),
('sm-00015-0000-0000-000000000015', '44444444-4444-4444-4444-444444444444', '2026-06-25', 'LUNCH',     'ACTIVE',    NULL);


-- ============================================================================
-- 6. EXPENSES (operational costs)
-- ============================================================================
INSERT INTO `expenses` (`id`, `name`, `category`, `amount`, `description`, `expense_date`, `created_by`) VALUES
('ex-00001-0000-0000-000000000001', 'Monthly Rice Purchase',    'FOOD_PURCHASE',  15000.00, 'Rice and grains for June',            '2026-06-01', '22222222-2222-2222-2222-222222222222'),
('ex-00002-0000-0000-000000000002', 'Fish and Meat Purchase',   'FOOD_PURCHASE',  12000.00, 'Weekly protein purchase (week 1)',     '2026-06-03', '22222222-2222-2222-2222-222222222222'),
('ex-00003-0000-0000-000000000003', 'Vegetable Purchase',       'FOOD_PURCHASE',   5000.00, 'Fresh vegetables for the week',       '2026-06-05', '22222222-2222-2222-2222-222222222222'),
('ex-00004-0000-0000-000000000004', 'Gas Bill',                 'UTILITIES',       3500.00, 'Monthly gas consumption',             '2026-06-10', '22222222-2222-2222-2222-222222222222'),
('ex-00005-0000-0000-000000000005', 'Electricity Bill',         'UTILITIES',       4200.00, 'Monthly electricity bill',            '2026-06-10', '22222222-2222-2222-2222-222222222222'),
('ex-00006-0000-0000-000000000006', 'Cook Salary',              'SALARY',         20000.00, 'Monthly salary for 2 kitchen staff',  '2026-06-15', '22222222-2222-2222-2222-222222222222'),
('ex-00007-0000-0000-000000000007', 'Helper Salary',            'SALARY',         12000.00, 'Monthly salary for 2 helpers',        '2026-06-15', '22222222-2222-2222-2222-222222222222'),
('ex-00008-0000-0000-000000000008', 'Fish and Meat (week 2)',   'FOOD_PURCHASE',  11500.00, 'Weekly protein purchase (week 2)',     '2026-06-10', '22222222-2222-2222-2222-222222222222'),
('ex-00009-0000-0000-000000000009', 'New Utensils',             'EQUIPMENT',       3000.00, 'Replacement cooking pots',            '2026-06-18', '22222222-2222-2222-2222-222222222222'),
('ex-00010-0000-0000-000000000010', 'Plumbing Repair',          'MAINTENANCE',     2500.00, 'Kitchen sink plumbing fix',           '2026-06-20', '22222222-2222-2222-2222-222222222222');


-- ============================================================================
-- 7. EARNINGS (income sources)
-- ============================================================================
INSERT INTO `earnings` (`id`, `description`, `category`, `amount`, `earning_date`, `notes`, `created_by`) VALUES
('ea-00001-0000-0000-000000000001', 'June Meal Payments (Batch 1)', 'MEAL_PAYMENT', 45000.00, '2026-06-05', 'Collected from 30 customers',       '22222222-2222-2222-2222-222222222222'),
('ea-00002-0000-0000-000000000002', 'June Meal Payments (Batch 2)', 'MEAL_PAYMENT', 35000.00, '2026-06-15', 'Collected from remaining customers', '22222222-2222-2222-2222-222222222222'),
('ea-00003-0000-0000-000000000003', 'Security Deposit Collection',  'DEPOSIT',       5000.00, '2026-06-01', 'New customer deposits',             '22222222-2222-2222-2222-222222222222'),
('ea-00004-0000-0000-000000000004', 'University Grant',             'GRANT',        20000.00, '2026-06-10', 'Monthly hall dining subsidy',       '22222222-2222-2222-2222-222222222222'),
('ea-00005-0000-0000-000000000005', 'Non-Customer Meal Fees',       'OTHER',         2400.00, '2026-06-20', 'Guest meal request payments',       '22222222-2222-2222-2222-222222222222');


-- ============================================================================
-- 8. PAYMENTS (for non-customer meal requests)
-- ============================================================================
INSERT INTO `payments` (`id`, `user_id`, `request_id`, `amount`, `payment_method`, `reference_no`, `status`, `note`) VALUES
('py-00001-0000-0000-000000000001', '55555555-5555-5555-5555-555555555555', NULL, 80.00, 'MOBILE_BANKING', 'TXN847291', 'COMPLETED', 'bKash payment for lunch'),
('py-00002-0000-0000-000000000002', '55555555-5555-5555-5555-555555555555', NULL, 80.00, 'CASH',           NULL,         'COMPLETED', 'Cash payment at counter'),
('py-00003-0000-0000-000000000003', '66666666-6666-6666-6666-666666666666', NULL, 80.00, 'BANK_TRANSFER',  'REF-0055',   'PENDING',   'Pending bank transfer'),
('py-00004-0000-0000-000000000004', '66666666-6666-6666-6666-666666666666', NULL, 80.00, 'MOBILE_BANKING', 'TXN923104',  'COMPLETED', 'Nagad payment');


-- ============================================================================
-- 9. MEAL REQUESTS (non-customer one-time meal requests)
-- ============================================================================
INSERT INTO `meal_requests` (`id`, `user_id`, `date`, `meal_type`, `reason`, `status`, `payment_id`, `reviewed_by`, `reviewed_at`, `rejection_note`) VALUES
('mr-00001-0000-0000-000000000001', '55555555-5555-5555-5555-555555555555', '2026-06-24', 'LUNCH',     'Attending IRE department seminar',        'APPROVED',         'py-00001-0000-0000-000000000001', '22222222-2222-2222-2222-222222222222', '2026-06-23 15:00:00', NULL),
('mr-00002-0000-0000-000000000002', '55555555-5555-5555-5555-555555555555', '2026-06-25', 'DINNER',    'Lab work running late',                  'PENDING_APPROVAL',  'py-00002-0000-0000-000000000002', NULL, NULL, NULL),
('mr-00003-0000-0000-000000000003', '66666666-6666-6666-6666-666666666666', '2026-06-24', 'BREAKFAST', 'Morning exam at hall campus',             'PENDING_PAYMENT',   NULL, NULL, NULL, NULL),
('mr-00004-0000-0000-000000000004', '66666666-6666-6666-6666-666666666666', '2026-06-23', 'LUNCH',     'Visiting friends at the hall',            'REJECTED',          'py-00004-0000-0000-000000000004', '22222222-2222-2222-2222-222222222222', '2026-06-22 10:00:00', 'Insufficient justification'),
('mr-00005-0000-0000-000000000005', '55555555-5555-5555-5555-555555555555', '2026-06-26', 'LUNCH',     'Department meeting at hall',              'CANCELLED',         NULL, NULL, NULL, NULL);


-- ============================================================================
-- 10. MEMBER PAYMENTS (monthly payment tracking for customers)
-- ============================================================================
INSERT INTO `member_payments` (`id`, `user_id`, `year`, `month`, `amount_due`, `amount_paid`, `status`) VALUES
('mp-00001-0000-0000-000000000001', '33333333-3333-3333-3333-333333333333', 2026, 5, 3500.00, 3500.00, 'PAID'),
('mp-00002-0000-0000-000000000002', '33333333-3333-3333-3333-333333333333', 2026, 6, 3500.00, 2000.00, 'PENDING'),
('mp-00003-0000-0000-000000000003', '44444444-4444-4444-4444-444444444444', 2026, 5, 3500.00, 3500.00, 'PAID'),
('mp-00004-0000-0000-000000000004', '44444444-4444-4444-4444-444444444444', 2026, 6, 3500.00,    0.00, 'PENDING');


-- ============================================================================
-- 11. PAYMENT PROOFS (evidence of payment submitted by customers)
-- ============================================================================
INSERT INTO `payment_proofs` (`id`, `member_payment_id`, `user_id`, `proof_type`, `proof_value`, `status`, `reviewed_by`, `reviewed_at`, `rejection_note`) VALUES
('pp-00001-0000-0000-000000000001', 'mp-00001-0000-0000-000000000001', '33333333-3333-3333-3333-333333333333', 'TRANSACTION_ID', 'TXN-BKASH-20260515-7842',                 'APPROVED',  '22222222-2222-2222-2222-222222222222', '2026-05-16 09:00:00', NULL),
('pp-00002-0000-0000-000000000002', 'mp-00002-0000-0000-000000000002', '33333333-3333-3333-3333-333333333333', 'IMAGE',          '/uploads/proofs/arif_june_bkash.jpg',     'SUBMITTED', NULL, NULL, NULL),
('pp-00003-0000-0000-000000000003', 'mp-00003-0000-0000-000000000003', '44444444-4444-4444-4444-444444444444', 'TEXT_NOTE',       'Paid via Nagad to 01711000002 on May 14', 'APPROVED',  '22222222-2222-2222-2222-222222222222', '2026-05-15 10:30:00', NULL),
('pp-00004-0000-0000-000000000004', 'mp-00004-0000-0000-000000000004', '44444444-4444-4444-4444-444444444444', 'TRANSACTION_ID', 'TXN-NAGAD-20260620-1234',                 'REJECTED',  '22222222-2222-2222-2222-222222222222', '2026-06-21 14:00:00', 'Transaction ID does not match our records');


-- ============================================================================
-- 12. AUDIT LOGS (system activity records)
-- ============================================================================
INSERT INTO `audit_logs` (`user_id`, `action`, `entity_type`, `entity_id`, `old_value`, `new_value`, `ip_address`, `user_agent`) VALUES
('11111111-1111-1111-1111-111111111111', 'USER_CREATED',      'User',          '22222222-2222-2222-2222-222222222222', NULL,
 '{"description": "Dining Manager account created"}', '127.0.0.1', 'Mozilla/5.0'),
('11111111-1111-1111-1111-111111111111', 'MANAGER_ASSIGNED',  'User',          '22222222-2222-2222-2222-222222222222',
 '{"role": "NON_CUSTOMER"}', '{"role": "DINING_MANAGER"}', '127.0.0.1', 'Mozilla/5.0'),
('22222222-2222-2222-2222-222222222222', 'MENU_CREATED',      'DailyMenu',     'dm-00001-0000-0000-000000000001', NULL,
 '{"date": "2026-06-23", "meal_type": "BREAKFAST"}', '192.168.1.10', 'Mozilla/5.0'),
('22222222-2222-2222-2222-222222222222', 'CUSTOMER_ADDED',    'User',          '33333333-3333-3333-3333-333333333333',
 '{"role": "NON_CUSTOMER"}', '{"role": "CUSTOMER"}', '192.168.1.10', 'Mozilla/5.0'),
('22222222-2222-2222-2222-222222222222', 'EXPENSE_CREATED',   'Expense',       'ex-00001-0000-0000-000000000001', NULL,
 '{"name": "Monthly Rice Purchase", "amount": 15000.00}', '192.168.1.10', 'Mozilla/5.0'),
('33333333-3333-3333-3333-333333333333', 'MEAL_ADDED',        'StudentMeal',   'sm-00001-0000-0000-000000000001', NULL,
 '{"date": "2026-06-23", "meal_type": "BREAKFAST"}', '10.0.0.5', 'Mozilla/5.0'),
('33333333-3333-3333-3333-333333333333', 'MEAL_CANCELLED',    'StudentMeal',   'sm-00003-0000-0000-000000000003',
 '{"status": "ACTIVE"}', '{"status": "CANCELLED"}', '10.0.0.5', 'Mozilla/5.0'),
('11111111-1111-1111-1111-111111111111', 'SETTINGS_UPDATED',  'SystemSetting', NULL, NULL,
 '{"description": "Initial system settings configured"}', '127.0.0.1', 'Mozilla/5.0');


-- ============================================================================
-- 13. SYSTEM SETTINGS (application configuration)
-- ============================================================================
INSERT INTO `system_settings` (`key_name`, `value`, `description`, `updated_by`) VALUES
('meal_price_non_customer',  '80.00',                                  'Price per meal for non-customer requests (BDT)',       '11111111-1111-1111-1111-111111111111'),
('max_meals_per_day',        '3',                                      'Maximum meals a customer can enroll in per day',       '11111111-1111-1111-1111-111111111111'),
('allow_same_day_requests',  'true',                                   'Allow non-customers to request meals on same day',     '11111111-1111-1111-1111-111111111111'),
('auto_approve_requests',    'false',                                  'Automatically approve non-customer requests after payment', '11111111-1111-1111-1111-111111111111'),
('site_name',                'University Dining Management System',    'Application display name',                            '11111111-1111-1111-1111-111111111111'),
('academic_year',            '2024-2025',                              'Current academic year',                               '11111111-1111-1111-1111-111111111111'),
('contact_email',            'dining@university.edu',                  'Dining office contact email',                         '11111111-1111-1111-1111-111111111111'),
('notice_board',             '',                                       'Public notice visible on dashboard',                  '11111111-1111-1111-1111-111111111111');


SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- Sample data loaded — 6 users, 3 schedules, 9 menus, 24 menu items,
-- 15 student meals, 10 expenses, 5 earnings, 4 payments, 5 meal requests,
-- 4 member payments, 4 payment proofs, 8 audit logs, 8 system settings
-- ============================================================================
