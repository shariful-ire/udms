#!/usr/bin/env python3
"""
Seed the UDMS database with test accounts and sample data.

Usage:
    python scripts/seed_db.py

Test accounts created:
    provost         / Admin@1234!    (Provost)
    diningmgr       / Manager@1234!  (Dining Manager)
    student_customer/ Student@1234!  (Customer)
    student_normal  / Student@1234!  (Non-Customer)
"""
import asyncio
import random
import sys
import os
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal, engine
from app.db.base import Base
from app.models.user import User, RefreshToken
from app.models.meal import MealSchedule, DailyMenu, MenuItem, StudentMeal
from app.models.expense import Expense, AuditLog, SystemSetting
from app.models.expense import MealRequest, Payment

UTC = timezone.utc


# ─── Helpers ──────────────────────────────────────────────────────────────────

def make_user(
    *,
    student_id: str,
    username: str,
    full_name: str,
    email: str,
    password: str,
    role: str,
    department: str,
    batch: str,
    hall_name: str,
    status: str = "ACTIVE",
    email_verified: bool = True,
) -> User:
    return User(
        student_id=student_id,
        username=username,
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
        role=role,
        department=department,
        batch=batch,
        hall_name=hall_name,
        status=status,
        email_verified=email_verified,
        failed_attempts=0,
    )


DEPARTMENTS = ["CSE", "EEE", "ME", "CE", "BBA", "English", "Physics", "Chemistry", "Math", "Law"]
HALLS = ["Shaheed Hall", "Bangabandhu Hall", "Shahjalal Hall", "Rokeya Hall", "Sobhanbag Hall"]
FOOD_ITEMS = {
    "BREAKFAST": [
        ("Paratha", "2 pieces"), ("Egg Fry", "1 piece"), ("Tea", "1 cup"),
        ("Halwa", "1 bowl"), ("Puri", "3 pieces"), ("Lassi", "1 glass"),
    ],
    "LUNCH": [
        ("Rice", "1 plate"), ("Dal", "1 bowl"), ("Fish Curry", "2 pieces"),
        ("Vegetable", "1 bowl"), ("Salad", "1 bowl"), ("Water", "1 bottle"),
        ("Chicken Curry", "2 pieces"), ("Beef Bhuna", "150g"),
    ],
    "DINNER": [
        ("Rice", "1 plate"), ("Dal", "1 bowl"), ("Chicken Roast", "1 piece"),
        ("Mixed Vegetable", "1 bowl"), ("Fruit", "seasonal"),
        ("Beef Curry", "150g"), ("Egg Curry", "2 pieces"),
    ],
}
EXPENSE_NAMES = [
    ("Monthly Rice Purchase", "FOOD_PURCHASE", "Rice and grains for the month"),
    ("Fish and Meat Purchase", "FOOD_PURCHASE", "Weekly protein purchase"),
    ("Vegetable Purchase", "FOOD_PURCHASE", "Fresh vegetables for cooking"),
    ("Gas Bill", "UTILITIES", "Monthly gas consumption"),
    ("Electricity Bill", "UTILITIES", "Monthly electricity bill"),
    ("Water Bill", "UTILITIES", "Monthly water consumption"),
    ("Cook Salary", "SALARY", "Monthly salary for kitchen staff"),
    ("Helper Salary", "SALARY", "Monthly salary for helpers"),
    ("Gas Burner Repair", "EQUIPMENT", "Kitchen equipment maintenance"),
    ("New Utensils", "EQUIPMENT", "Replacement cooking utensils"),
    ("Plumbing Repair", "MAINTENANCE", "Bathroom and kitchen plumbing"),
    ("Hall Cleaning", "MAINTENANCE", "Cleaning supplies and services"),
    ("Miscellaneous Supplies", "MISCELLANEOUS", "Various small purchases"),
]


async def clear_existing(db: AsyncSession) -> None:
    """Remove all existing data (preserves schema)."""
    print("  Clearing existing data...")
    from sqlalchemy import text
    await db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    for table in [
        "audit_logs", "system_settings", "payments", "meal_requests",
        "student_meals", "menu_items", "daily_menus", "meal_schedules",
        "refresh_tokens", "users",
    ]:
        try:
            await db.execute(text(f"TRUNCATE TABLE {table}"))
        except Exception:
            await db.execute(text(f"DELETE FROM {table}"))
    await db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    await db.commit()
    print("  ✓ Cleared existing data")


async def seed_users(db: AsyncSession) -> dict[str, User]:
    """Create the 4 core test accounts + 20 additional students."""
    print("  Seeding users...")
    users = {}

    # ── Core accounts ──────────────────────────────────────────────────────
    provost = make_user(
        student_id="PROVOST-001",
        username="provost",
        full_name="Prof. Dr. Rahman Ali",
        email="provost@university.edu",
        password="Admin@1234!",
        role="PROVOST",
        department="Administration",
        batch="N/A",
        hall_name="Administration Block",
    )
    db.add(provost)
    users["provost"] = provost

    manager = make_user(
        student_id="STAFF-001",
        username="diningmgr",
        full_name="Karim Hossain",
        email="manager@university.edu",
        password="Manager@1234!",
        role="DINING_MANAGER",
        department="Dining Services",
        batch="N/A",
        hall_name="Dining Hall",
    )
    db.add(manager)
    users["manager"] = manager

    customer = make_user(
        student_id="CSE-2001-001",
        username="student_customer",
        full_name="Arif Hasan",
        email="customer@university.edu",
        password="Student@1234!",
        role="CUSTOMER",
        department="CSE",
        batch="2020",
        hall_name="Shaheed Hall",
    )
    db.add(customer)
    users["customer"] = customer

    normal = make_user(
        student_id="EEE-2001-002",
        username="student_normal",
        full_name="Nadia Islam",
        email="normal@university.edu",
        password="Student@1234!",
        role="NON_CUSTOMER",
        department="EEE",
        batch="2021",
        hall_name="Rokeya Hall",
    )
    db.add(normal)
    users["normal"] = normal

    await db.flush()

    # ── 20 additional students ─────────────────────────────────────────────
    first_names = ["Rahim", "Karim", "Salam", "Jahir", "Tania", "Sumaiya", "Mitu", "Rony",
                   "Anik", "Priya", "Rafiq", "Sadia", "Bilal", "Tasnim", "Imran", "Fariha",
                   "Rubel", "Nasrin", "Hasan", "Jerin"]
    last_names = ["Ahmed", "Khan", "Islam", "Hossain", "Akter", "Begum", "Rahman", "Chowdhury",
                  "Mia", "Sultana", "Ali", "Sheikh", "Mondal", "Das", "Sarker", "Roy",
                  "Bhuiyan", "Khatun", "Babu", "Jahan"]
    extra_students: list[User] = []
    for i, (first, last) in enumerate(zip(first_names, last_names), start=3):
        dept = random.choice(DEPARTMENTS)
        batch = str(random.randint(2018, 2023))
        hall = random.choice(HALLS)
        role = "CUSTOMER" if i % 2 == 0 else "NON_CUSTOMER"
        u = make_user(
            student_id=f"{dept}-20{i:02d}-{i:03d}",
            username=f"{first.lower()}{i:03d}",
            full_name=f"{first} {last}",
            email=f"{first.lower()}.{last.lower()}{i}@university.edu",
            password="Student@1234!",
            role=role,
            department=dept,
            batch=batch,
            hall_name=hall,
        )
        db.add(u)
        extra_students.append(u)

    await db.flush()
    users["extra"] = extra_students
    print(f"  ✓ Created {4 + len(extra_students)} users")
    return users


async def seed_meal_schedules(db: AsyncSession, created_by_id: str) -> None:
    """Create the 3 default meal schedules."""
    print("  Seeding meal schedules...")
    schedules = [
        MealSchedule(meal_type="BREAKFAST", start_time=time(7, 0),  end_time=time(9, 0),  cancel_deadline=time(6, 30),  is_active=True, created_by=created_by_id),
        MealSchedule(meal_type="LUNCH",     start_time=time(12, 0), end_time=time(14, 0), cancel_deadline=time(11, 30), is_active=True, created_by=created_by_id),
        MealSchedule(meal_type="DINNER",    start_time=time(19, 0), end_time=time(21, 0), cancel_deadline=time(18, 30), is_active=True, created_by=created_by_id),
    ]
    for s in schedules:
        db.add(s)
    await db.flush()
    print("  ✓ Created 3 meal schedules")


async def seed_daily_menus(db: AsyncSession, manager_id: str) -> None:
    """Create 7 days of daily menus (today ± 3 days)."""
    print("  Seeding daily menus...")
    today = date.today()
    count = 0
    for delta in range(-3, 4):
        d = today + timedelta(days=delta)
        for meal_type, items in FOOD_ITEMS.items():
            menu = DailyMenu(date=d, meal_type=meal_type, is_cancelled=False, created_by=manager_id)
            db.add(menu)
            await db.flush()
            for food_name, quantity in random.sample(items, min(len(items), random.randint(3, 5))):
                db.add(MenuItem(menu_id=menu.id, food_name=food_name, quantity=quantity))
            count += 1
    await db.flush()
    print(f"  ✓ Created {count} daily menus with items")


async def seed_meal_records(db: AsyncSession, users: dict) -> None:
    """Create 90 days of historical meal records for customer accounts."""
    print("  Seeding meal records (90 days history)...")
    today = date.today()
    meal_types = ["BREAKFAST", "LUNCH", "DINNER"]

    customer_users = [users["customer"]] + [u for u in users["extra"] if u.role == "CUSTOMER"]
    count = 0

    for user in customer_users:
        for delta in range(-90, 1):
            d = today + timedelta(days=delta)
            for meal_type in meal_types:
                # ~70% attendance rate
                if random.random() < 0.7:
                    # ~10% cancellation rate
                    status = "CANCELLED" if random.random() < 0.1 else "ACTIVE"
                    sm = StudentMeal(
                        user_id=user.id,
                        date=d,
                        meal_type=meal_type,
                        status=status,
                        cancelled_at=datetime.now(UTC) if status == "CANCELLED" else None,
                    )
                    db.add(sm)
                    count += 1

    await db.flush()
    print(f"  ✓ Created {count} meal records")


async def seed_expenses(db: AsyncSession, manager_id: str) -> None:
    """Create 30 days of expense records."""
    print("  Seeding expenses...")
    today = date.today()
    count = 0
    for delta in range(-30, 1):
        d = today + timedelta(days=delta)
        num_expenses = random.randint(1, 3)
        for _ in range(num_expenses):
            name, category, description = random.choice(EXPENSE_NAMES)
            amount = Decimal(str(round(random.uniform(500, 15000), 2)))
            db.add(Expense(
                name=f"{name} — {d.strftime('%b %d')}",
                category=category,
                amount=amount,
                description=description,
                expense_date=d,
                created_by=manager_id,
            ))
            count += 1

    await db.flush()
    print(f"  ✓ Created {count} expense records")


async def seed_meal_requests(db: AsyncSession, users: dict) -> None:
    """Create 10 pending meal requests at various stages."""
    print("  Seeding meal requests...")
    today = date.today()
    normal_users = [users["normal"]] + [u for u in users["extra"] if u.role == "NON_CUSTOMER"]
    meal_types = ["BREAKFAST", "LUNCH", "DINNER"]
    statuses = [
        "PENDING_PAYMENT", "PENDING_PAYMENT",
        "PENDING_APPROVAL", "PENDING_APPROVAL", "PENDING_APPROVAL",
        "APPROVED", "APPROVED", "APPROVED",
        "REJECTED",
        "CANCELLED",
    ]

    for i, status in enumerate(statuses):
        user = normal_users[i % len(normal_users)]
        d = today + timedelta(days=random.randint(-5, 7))
        meal_type = random.choice(meal_types)

        request = MealRequest(
            user_id=user.id,
            date=d,
            meal_type=meal_type,
            reason=f"Attending a departmental event on {d}",
            status=status,
        )

        if status in ("PENDING_APPROVAL", "APPROVED", "REJECTED"):
            payment = Payment(
                user_id=user.id,
                amount=Decimal("80.00"),
                payment_method=random.choice(["CASH", "MOBILE_BANKING", "BANK_TRANSFER"]),
                reference_no=f"TXN{random.randint(100000, 999999)}",
                status="COMPLETED",
            )
            db.add(payment)
            await db.flush()
            request.payment_id = payment.id

        if status in ("APPROVED", "REJECTED"):
            request.reviewed_by = users["manager"].id
            request.reviewed_at = datetime.now(UTC)

        if status == "REJECTED":
            request.rejection_note = "Insufficient justification or date conflict."

        db.add(request)

        # Create student meal record for approved requests
        if status == "APPROVED":
            db.add(StudentMeal(
                user_id=user.id,
                date=d,
                meal_type=meal_type,
                status="ACTIVE",
            ))

    await db.flush()
    print("  ✓ Created 10 meal requests")


async def seed_system_settings(db: AsyncSession, provost_id: str) -> None:
    """Insert default system settings."""
    defaults = [
        ("meal_price_non_customer", "80.00", "Price per meal for non-customer requests (BDT)"),
        ("max_meals_per_day", "3", "Maximum meals a customer can enroll per day"),
        ("allow_same_day_requests", "true", "Allow non-customers to request meals same day"),
        ("auto_approve_requests", "false", "Automatically approve after payment"),
        ("site_name", "University Dining Management System", "Application name"),
        ("academic_year", "2024-2025", "Current academic year"),
        ("contact_email", "dining@university.edu", "Dining office contact email"),
        ("notice_board", "", "Public notice visible on dashboard"),
    ]
    for key, value, description in defaults:
        db.add(SystemSetting(key_name=key, value=value, description=description, updated_by=provost_id))
    await db.flush()
    print("  ✓ Created system settings")


async def seed_audit_logs(db: AsyncSession, provost_id: str, manager_id: str) -> None:
    """Create a few historical audit log entries."""
    events = [
        (provost_id, "USER_CREATED", "User", "Initial provost account created"),
        (provost_id, "MANAGER_ASSIGNED", "User", "Dining Manager assigned"),
        (manager_id, "MENU_CREATED", "DailyMenu", "7 days of menus created"),
        (manager_id, "CUSTOMER_ADDED", "User", "Batch of students enrolled as customers"),
        (provost_id, "SETTINGS_UPDATED", "SystemSetting", "Initial system settings configured"),
        (manager_id, "EXPENSE_CREATED", "Expense", "Monthly expenses logged"),
        (provost_id, "REPORT_GENERATED", "Report", "Monthly dining report generated"),
    ]
    for user_id, action, entity_type, description in events:
        db.add(AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            new_value={"description": description},
            ip_address="127.0.0.1",
        ))
    await db.flush()
    print("  ✓ Created audit log entries")


async def run_seed() -> None:
    """Main seed runner."""
    print("\n🌱 UDMS Database Seeder\n" + "=" * 40)

    async with AsyncSessionLocal() as db:
        try:
            await clear_existing(db)

            users = await seed_users(db)
            await db.commit()

            await seed_meal_schedules(db, users["manager"].id)
            await seed_daily_menus(db, users["manager"].id)
            await seed_meal_records(db, users)
            await seed_expenses(db, users["manager"].id)
            await seed_meal_requests(db, users)
            await seed_system_settings(db, users["provost"].id)
            await seed_audit_logs(db, users["provost"].id, users["manager"].id)

            await db.commit()

            print("\n✅ Seeding complete!\n")
            print("Test Accounts:")
            print("─" * 60)
            print(f"  Provost:    provost         / Admin@1234!")
            print(f"  Manager:    diningmgr       / Manager@1234!")
            print(f"  Customer:   student_customer / Student@1234!")
            print(f"  Non-Cust:   student_normal   / Student@1234!")
            print("─" * 60)

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Seeding failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_seed())
