-- ============================================================================
-- UDMS — University Dining Management System
-- Complete MySQL Database Schema
-- ============================================================================
-- Generated from SQLAlchemy models + Alembic migration (source of truth)
-- Compatible with: MySQL 8.0 / XAMPP phpMyAdmin
-- Charset: utf8mb4 | Collation: utf8mb4_unicode_ci | Engine: InnoDB
-- ============================================================================

-- Create and select the database
CREATE DATABASE IF NOT EXISTS `udms`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `udms`;

-- Disable FK checks during table creation (order-independent)
SET FOREIGN_KEY_CHECKS = 0;


-- ============================================================================
-- TABLE 1: users
-- Central user table — stores all accounts (Provost, Manager, Customer, Non-Customer)
-- ============================================================================
CREATE TABLE `users` (
  `id`              VARCHAR(36)   NOT NULL,
  `student_id`      VARCHAR(20)   NOT NULL,
  `username`        VARCHAR(50)   NOT NULL,
  `full_name`       VARCHAR(150)  NOT NULL,
  `email`           VARCHAR(255)  NOT NULL,
  `password_hash`   VARCHAR(255)  NOT NULL,
  `role`            ENUM('PROVOST','DINING_MANAGER','CUSTOMER','NON_CUSTOMER')
                                  NOT NULL DEFAULT 'NON_CUSTOMER',
  `department`      VARCHAR(100)  DEFAULT NULL,
  `batch`           VARCHAR(20)   DEFAULT NULL,
  `hall_name`       VARCHAR(100)  DEFAULT NULL,
  `phone`           VARCHAR(20)   DEFAULT NULL,
  `profile_image`   VARCHAR(500)  DEFAULT NULL,
  `status`          ENUM('ACTIVE','INACTIVE','SUSPENDED')
                                  NOT NULL DEFAULT 'INACTIVE',
  `email_verified`  TINYINT(1)    NOT NULL DEFAULT 0,
  `failed_attempts` INT           NOT NULL DEFAULT 0,
  `locked_until`    DATETIME      DEFAULT NULL,
  `last_login`      DATETIME      DEFAULT NULL,
  `created_at`      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
                                  ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_users_student_id` (`student_id`),
  UNIQUE KEY `uq_users_username`   (`username`),
  UNIQUE KEY `uq_users_email`      (`email`),

  INDEX `idx_users_student_id` (`student_id`),
  INDEX `idx_users_username`   (`username`),
  INDEX `idx_users_email`      (`email`),
  INDEX `idx_users_role`       (`role`),
  INDEX `idx_users_status`     (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- TABLE 2: refresh_tokens
-- Stores hashed JWT refresh tokens for session management
-- ============================================================================
CREATE TABLE `refresh_tokens` (
  `id`          VARCHAR(36)   NOT NULL,
  `user_id`     VARCHAR(36)   NOT NULL,
  `token_hash`  VARCHAR(255)  NOT NULL,
  `expires_at`  DATETIME      NOT NULL,
  `created_at`  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_rt_token_hash` (`token_hash`),

  INDEX `idx_rt_user_id`  (`user_id`),
  INDEX `idx_rt_expires`  (`expires_at`),

  CONSTRAINT `fk_rt_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- TABLE 3: meal_schedules
-- Defines time windows for each meal type (one row per BREAKFAST/LUNCH/DINNER)
-- ============================================================================
CREATE TABLE `meal_schedules` (
  `id`               VARCHAR(36)   NOT NULL,
  `meal_type`        ENUM('BREAKFAST','LUNCH','DINNER') NOT NULL,
  `start_time`       TIME          NOT NULL,
  `end_time`         TIME          NOT NULL,
  `cancel_deadline`  TIME          NOT NULL,
  `is_active`        TINYINT(1)    NOT NULL DEFAULT 1,
  `created_by`       VARCHAR(36)   NOT NULL,
  `updated_by`       VARCHAR(36)   DEFAULT NULL,
  `created_at`       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
                                   ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_ms_meal_type` (`meal_type`),

  INDEX `idx_ms_active` (`is_active`),

  CONSTRAINT `fk_ms_created_by`
    FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_ms_updated_by`
    FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- TABLE 4: daily_menus
-- One row per date + meal_type combination; can be cancelled by manager
-- ============================================================================
CREATE TABLE `daily_menus` (
  `id`            VARCHAR(36)   NOT NULL,
  `date`          DATE          NOT NULL,
  `meal_type`     ENUM('BREAKFAST','LUNCH','DINNER') NOT NULL,
  `is_cancelled`  TINYINT(1)    NOT NULL DEFAULT 0,
  `created_by`    VARCHAR(36)   NOT NULL,
  `updated_by`    VARCHAR(36)   DEFAULT NULL,
  `created_at`    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_date_meal_type` (`date`, `meal_type`),

  INDEX `idx_dm_date` (`date`),

  CONSTRAINT `fk_dm_created_by`
    FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_dm_updated_by`
    FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- TABLE 5: menu_items
-- Individual food items belonging to a daily menu
-- ============================================================================
CREATE TABLE `menu_items` (
  `id`          VARCHAR(36)   NOT NULL,
  `menu_id`     VARCHAR(36)   NOT NULL,
  `food_name`   VARCHAR(200)  NOT NULL,
  `quantity`    VARCHAR(100)  DEFAULT NULL,
  `notes`       TEXT          DEFAULT NULL,
  `created_at`  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),

  INDEX `idx_mi_menu_id` (`menu_id`),

  CONSTRAINT `fk_mi_menu`
    FOREIGN KEY (`menu_id`) REFERENCES `daily_menus` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- TABLE 6: student_meals
-- Tracks each customer's meal enrollment per date + meal_type
-- ============================================================================
CREATE TABLE `student_meals` (
  `id`            VARCHAR(36)   NOT NULL,
  `user_id`       VARCHAR(36)   NOT NULL,
  `date`          DATE          NOT NULL,
  `meal_type`     ENUM('BREAKFAST','LUNCH','DINNER') NOT NULL,
  `status`        ENUM('ACTIVE','CANCELLED') NOT NULL DEFAULT 'ACTIVE',
  `cancelled_at`  DATETIME      DEFAULT NULL,
  `created_at`    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_user_date_meal` (`user_id`, `date`, `meal_type`),

  INDEX `idx_sm_user_id` (`user_id`),
  INDEX `idx_sm_date`    (`date`),
  INDEX `idx_sm_status`  (`status`),

  CONSTRAINT `fk_sm_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- TABLE 7: payments
-- Stores payment transactions (linked to meal requests for non-customers)
-- ============================================================================
CREATE TABLE `payments` (
  `id`              VARCHAR(36)   NOT NULL,
  `user_id`         VARCHAR(36)   NOT NULL,
  `request_id`      VARCHAR(36)   DEFAULT NULL,
  `amount`          DECIMAL(10,2) NOT NULL,
  `payment_method`  ENUM('CASH','MOBILE_BANKING','BANK_TRANSFER','OTHER') NOT NULL,
  `reference_no`    VARCHAR(100)  DEFAULT NULL,
  `status`          ENUM('PENDING','COMPLETED','FAILED','REFUNDED')
                                  NOT NULL DEFAULT 'PENDING',
  `note`            TEXT          DEFAULT NULL,
  `created_at`      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
                                  ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),

  INDEX `idx_pay_user_id`  (`user_id`),
  INDEX `idx_pay_status`   (`status`),
  INDEX `idx_pay_created`  (`created_at`),

  CONSTRAINT `fk_pay_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- TABLE 8: meal_requests
-- Non-customer meal requests with approval workflow
-- ============================================================================
CREATE TABLE `meal_requests` (
  `id`              VARCHAR(36)   NOT NULL,
  `user_id`         VARCHAR(36)   NOT NULL,
  `date`            DATE          NOT NULL,
  `meal_type`       ENUM('BREAKFAST','LUNCH','DINNER') NOT NULL,
  `reason`          TEXT          DEFAULT NULL,
  `status`          ENUM('PENDING_PAYMENT','PENDING_APPROVAL','APPROVED','REJECTED','CANCELLED')
                                  NOT NULL DEFAULT 'PENDING_PAYMENT',
  `payment_id`      VARCHAR(36)   DEFAULT NULL,
  `reviewed_by`     VARCHAR(36)   DEFAULT NULL,
  `reviewed_at`     DATETIME      DEFAULT NULL,
  `rejection_note`  TEXT          DEFAULT NULL,
  `created_at`      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
                                  ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),

  INDEX `idx_mr_user_id` (`user_id`),
  INDEX `idx_mr_status`  (`status`),
  INDEX `idx_mr_date`    (`date`),

  CONSTRAINT `fk_mr_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_mr_payment`
    FOREIGN KEY (`payment_id`) REFERENCES `payments` (`id`),
  CONSTRAINT `fk_mr_reviewer`
    FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- TABLE 9: expenses
-- Dining hall operational expenses categorized by type
-- ============================================================================
CREATE TABLE `expenses` (
  `id`            VARCHAR(36)    NOT NULL,
  `name`          VARCHAR(200)   NOT NULL,
  `category`      ENUM('FOOD_PURCHASE','UTILITIES','SALARY','EQUIPMENT','MAINTENANCE','MISCELLANEOUS')
                                 NOT NULL,
  `amount`        DECIMAL(12,2)  NOT NULL,
  `description`   TEXT           DEFAULT NULL,
  `expense_date`  DATE           NOT NULL,
  `created_by`    VARCHAR(36)    NOT NULL,
  `updated_by`    VARCHAR(36)    DEFAULT NULL,
  `created_at`    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                 ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),

  INDEX `idx_exp_category`   (`category`),
  INDEX `idx_exp_date`       (`expense_date`),
  INDEX `idx_exp_created_by` (`created_by`),

  CONSTRAINT `fk_exp_created_by`
    FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_exp_updated_by`
    FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- TABLE 10: earnings
-- Income records (meal payments, deposits, grants)
-- ============================================================================
CREATE TABLE `earnings` (
  `id`            VARCHAR(36)    NOT NULL,
  `description`   VARCHAR(200)   NOT NULL,
  `category`      ENUM('MEAL_PAYMENT','DEPOSIT','GRANT','OTHER') NOT NULL,
  `amount`        DECIMAL(12,2)  NOT NULL,
  `earning_date`  DATE           NOT NULL,
  `notes`         TEXT           DEFAULT NULL,
  `created_by`    VARCHAR(36)    NOT NULL,
  `created_at`    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                 ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),

  INDEX `idx_earn_category`   (`category`),
  INDEX `idx_earn_date`       (`earning_date`),
  INDEX `idx_earn_created_by` (`created_by`),

  CONSTRAINT `fk_earn_created_by`
    FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- TABLE 11: member_payments
-- Monthly payment tracking per customer (one record per user + year + month)
-- ============================================================================
CREATE TABLE `member_payments` (
  `id`          VARCHAR(36)    NOT NULL,
  `user_id`     VARCHAR(36)    NOT NULL,
  `year`        INT            NOT NULL,
  `month`       INT            NOT NULL,
  `amount_due`  DECIMAL(12,2)  NOT NULL DEFAULT 0.00,
  `amount_paid` DECIMAL(12,2)  NOT NULL DEFAULT 0.00,
  `status`      ENUM('PAID','PENDING') NOT NULL DEFAULT 'PENDING',
  `created_at`  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP
                               ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_user_year_month` (`user_id`, `year`, `month`),

  INDEX `idx_mp_user_id` (`user_id`),
  INDEX `idx_mp_status`  (`status`),

  CONSTRAINT `fk_mp_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- TABLE 12: payment_proofs
-- Evidence submitted by customers to verify their monthly payments
-- ============================================================================
CREATE TABLE `payment_proofs` (
  `id`                 VARCHAR(36)   NOT NULL,
  `member_payment_id`  VARCHAR(36)   NOT NULL,
  `user_id`            VARCHAR(36)   NOT NULL,
  `proof_type`         ENUM('IMAGE','TRANSACTION_ID','TEXT_NOTE') NOT NULL,
  `proof_value`        TEXT          NOT NULL,
  `status`             ENUM('SUBMITTED','APPROVED','REJECTED')
                                     NOT NULL DEFAULT 'SUBMITTED',
  `reviewed_by`        VARCHAR(36)   DEFAULT NULL,
  `reviewed_at`        DATETIME      DEFAULT NULL,
  `rejection_note`     TEXT          DEFAULT NULL,
  `created_at`         DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),

  INDEX `idx_pp_member_payment` (`member_payment_id`),
  INDEX `idx_pp_user_id`        (`user_id`),
  INDEX `idx_pp_status`         (`status`),

  CONSTRAINT `fk_pp_member_payment`
    FOREIGN KEY (`member_payment_id`) REFERENCES `member_payments` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_pp_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_pp_reviewer`
    FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- TABLE 13: audit_logs
-- Immutable record of all significant system actions
-- ============================================================================
CREATE TABLE `audit_logs` (
  `id`          BIGINT        NOT NULL AUTO_INCREMENT,
  `user_id`     VARCHAR(36)   DEFAULT NULL,
  `action`      VARCHAR(100)  NOT NULL,
  `entity_type` VARCHAR(50)   NOT NULL,
  `entity_id`   VARCHAR(36)   DEFAULT NULL,
  `old_value`   JSON          DEFAULT NULL,
  `new_value`   JSON          DEFAULT NULL,
  `ip_address`  VARCHAR(45)   DEFAULT NULL,
  `user_agent`  VARCHAR(500)  DEFAULT NULL,
  `created_at`  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),

  INDEX `idx_al_user_id` (`user_id`),
  INDEX `idx_al_action`  (`action`),
  INDEX `idx_al_entity`  (`entity_type`, `entity_id`),
  INDEX `idx_al_created` (`created_at`),

  CONSTRAINT `fk_al_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- TABLE 14: system_settings
-- Key-value configuration store for runtime application settings
-- ============================================================================
CREATE TABLE `system_settings` (
  `id`          BIGINT        NOT NULL AUTO_INCREMENT,
  `key_name`    VARCHAR(100)  NOT NULL,
  `value`       TEXT          NOT NULL,
  `description` VARCHAR(500)  DEFAULT NULL,
  `updated_by`  VARCHAR(36)   DEFAULT NULL,
  `updated_at`  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
                              ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_ss_key_name` (`key_name`),

  CONSTRAINT `fk_ss_updated_by`
    FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Re-enable FK checks
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- Schema creation complete — 14 tables, 20 foreign keys, 9 unique constraints
-- ============================================================================
