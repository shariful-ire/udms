"""Initial database schema — all tables

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users ────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), nullable=False, default=sa.text("(UUID())")),
        sa.Column("student_id", sa.String(20), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("PROVOST", "DINING_MANAGER", "CUSTOMER", "NON_CUSTOMER", name="userrole"),
            nullable=False,
            server_default="NON_CUSTOMER",
        ),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("batch", sa.String(20), nullable=True),
        sa.Column("hall_name", sa.String(100), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("profile_image", sa.String(500), nullable=True),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "INACTIVE", "SUSPENDED", name="userstatus"),
            nullable=False,
            server_default="INACTIVE",
        ),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("failed_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(), nullable=True),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("idx_users_username", "users", ["username"])
    op.create_index("idx_users_email", "users", ["email"])
    op.create_index("idx_users_student_id", "users", ["student_id"])
    op.create_index("idx_users_role", "users", ["role"])
    op.create_index("idx_users_status", "users", ["status"])

    # ── refresh_tokens ───────────────────────────────────────────────────────
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.String(36), nullable=False, default=sa.text("(UUID())")),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_rt_user_id", "refresh_tokens", ["user_id"])
    op.create_index("idx_rt_expires", "refresh_tokens", ["expires_at"])

    # ── meal_schedules ───────────────────────────────────────────────────────
    op.create_table(
        "meal_schedules",
        sa.Column("id", sa.String(36), nullable=False, default=sa.text("(UUID())")),
        sa.Column("meal_type", sa.Enum("BREAKFAST", "LUNCH", "DINNER", name="mealtype"), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("cancel_deadline", sa.Time(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_by", sa.String(36), nullable=False),
        sa.Column("updated_by", sa.String(36), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("meal_type"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_ms_active", "meal_schedules", ["is_active"])

    # ── daily_menus ──────────────────────────────────────────────────────────
    op.create_table(
        "daily_menus",
        sa.Column("id", sa.String(36), nullable=False, default=sa.text("(UUID())")),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("meal_type", sa.Enum("BREAKFAST", "LUNCH", "DINNER", name="mealtype"), nullable=False),
        sa.Column("is_cancelled", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_by", sa.String(36), nullable=False),
        sa.Column("updated_by", sa.String(36), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("date", "meal_type", name="uq_date_meal_type"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_dm_date", "daily_menus", ["date"])

    # ── menu_items ───────────────────────────────────────────────────────────
    op.create_table(
        "menu_items",
        sa.Column("id", sa.String(36), nullable=False, default=sa.text("(UUID())")),
        sa.Column("menu_id", sa.String(36), nullable=False),
        sa.Column("food_name", sa.String(200), nullable=False),
        sa.Column("quantity", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["menu_id"], ["daily_menus.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_mi_menu_id", "menu_items", ["menu_id"])

    # ── student_meals ────────────────────────────────────────────────────────
    op.create_table(
        "student_meals",
        sa.Column("id", sa.String(36), nullable=False, default=sa.text("(UUID())")),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("meal_type", sa.Enum("BREAKFAST", "LUNCH", "DINNER", name="mealtype"), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "CANCELLED", name="mealstatus"),
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "date", "meal_type", name="uq_user_date_meal"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_sm_user_id", "student_meals", ["user_id"])
    op.create_index("idx_sm_date", "student_meals", ["date"])
    op.create_index("idx_sm_status", "student_meals", ["status"])

    # ── meal_requests ────────────────────────────────────────────────────────
    op.create_table(
        "meal_requests",
        sa.Column("id", sa.String(36), nullable=False, default=sa.text("(UUID())")),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("meal_type", sa.Enum("BREAKFAST", "LUNCH", "DINNER", name="mealtype"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING_PAYMENT",
                "PENDING_APPROVAL",
                "APPROVED",
                "REJECTED",
                "CANCELLED",
                name="requeststatus",
            ),
            nullable=False,
            server_default="PENDING_PAYMENT",
        ),
        sa.Column("payment_id", sa.String(36), nullable=True),
        sa.Column("reviewed_by", sa.String(36), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("rejection_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_mr_user_id", "meal_requests", ["user_id"])
    op.create_index("idx_mr_status", "meal_requests", ["status"])
    op.create_index("idx_mr_date", "meal_requests", ["date"])

    # ── payments ─────────────────────────────────────────────────────────────
    op.create_table(
        "payments",
        sa.Column("id", sa.String(36), nullable=False, default=sa.text("(UUID())")),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("request_id", sa.String(36), nullable=True),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "payment_method",
            sa.Enum("CASH", "MOBILE_BANKING", "BANK_TRANSFER", "OTHER", name="paymentmethod"),
            nullable=False,
        ),
        sa.Column("reference_no", sa.String(100), nullable=True),
        sa.Column(
            "status",
            sa.Enum("PENDING", "COMPLETED", "FAILED", "REFUNDED", name="paymentstatus"),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["request_id"], ["meal_requests.id"]),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_pay_user_id", "payments", ["user_id"])
    op.create_index("idx_pay_status", "payments", ["status"])
    op.create_index("idx_pay_created", "payments", ["created_at"])

    # ── expenses ─────────────────────────────────────────────────────────────
    op.create_table(
        "expenses",
        sa.Column("id", sa.String(36), nullable=False, default=sa.text("(UUID())")),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "FOOD_PURCHASE",
                "UTILITIES",
                "SALARY",
                "EQUIPMENT",
                "MAINTENANCE",
                "MISCELLANEOUS",
                name="expensecategory",
            ),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("created_by", sa.String(36), nullable=False),
        sa.Column("updated_by", sa.String(36), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_exp_category", "expenses", ["category"])
    op.create_index("idx_exp_date", "expenses", ["expense_date"])
    op.create_index("idx_exp_created_by", "expenses", ["created_by"])

    # ── audit_logs ───────────────────────────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=True),
        sa.Column("old_value", sa.JSON(), nullable=True),
        sa.Column("new_value", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_al_user_id", "audit_logs", ["user_id"])
    op.create_index("idx_al_action", "audit_logs", ["action"])
    op.create_index("idx_al_entity", "audit_logs", ["entity_type", "entity_id"])
    op.create_index("idx_al_created", "audit_logs", ["created_at"])

    # ── system_settings ──────────────────────────────────────────────────────
    op.create_table(
        "system_settings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("key_name", sa.String(100), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("updated_by", sa.String(36), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key_name"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )


def downgrade() -> None:
    op.drop_table("system_settings")
    op.drop_index("idx_al_created", "audit_logs")
    op.drop_index("idx_al_entity", "audit_logs")
    op.drop_index("idx_al_action", "audit_logs")
    op.drop_index("idx_al_user_id", "audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("idx_exp_created_by", "expenses")
    op.drop_index("idx_exp_date", "expenses")
    op.drop_index("idx_exp_category", "expenses")
    op.drop_table("expenses")
    op.drop_index("idx_pay_created", "payments")
    op.drop_index("idx_pay_status", "payments")
    op.drop_index("idx_pay_user_id", "payments")
    op.drop_table("payments")
    op.drop_index("idx_mr_date", "meal_requests")
    op.drop_index("idx_mr_status", "meal_requests")
    op.drop_index("idx_mr_user_id", "meal_requests")
    op.drop_table("meal_requests")
    op.drop_index("idx_sm_status", "student_meals")
    op.drop_index("idx_sm_date", "student_meals")
    op.drop_index("idx_sm_user_id", "student_meals")
    op.drop_table("student_meals")
    op.drop_index("idx_mi_menu_id", "menu_items")
    op.drop_table("menu_items")
    op.drop_index("idx_dm_date", "daily_menus")
    op.drop_table("daily_menus")
    op.drop_index("idx_ms_active", "meal_schedules")
    op.drop_table("meal_schedules")
    op.drop_index("idx_rt_expires", "refresh_tokens")
    op.drop_index("idx_rt_user_id", "refresh_tokens")
    op.drop_table("refresh_tokens")
    op.drop_index("idx_users_status", "users")
    op.drop_index("idx_users_role", "users")
    op.drop_index("idx_users_student_id", "users")
    op.drop_index("idx_users_email", "users")
    op.drop_index("idx_users_username", "users")
    op.drop_table("users")
