"""Database initialization — creates tables and seeds default data on first run."""
from __future__ import annotations

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import engine


async def create_tables() -> None:
    """Create all tables if they do not exist (development convenience)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables verified / created")


async def seed_default_settings(db: AsyncSession) -> None:
    """Insert default system settings if table is empty."""
    from app.models.expense import SystemSetting
    from sqlalchemy import select

    result = await db.execute(select(SystemSetting))
    if result.scalars().first():
        return  # Already seeded

    defaults = [
        ("meal_price_non_customer", "80.00", "Price per meal for non-customer requests (BDT)"),
        ("max_meals_per_day", "3", "Maximum meals a customer can enroll in per day"),
        ("allow_same_day_requests", "true", "Allow non-customers to request meals on same day"),
        ("auto_approve_requests", "false", "Automatically approve non-customer requests after payment"),
        ("site_name", "University Dining Management System", "Application display name"),
        ("academic_year", "2024-2025", "Current academic year"),
    ]

    for key, value, description in defaults:
        db.add(SystemSetting(key_name=key, value=value, description=description))

    await db.commit()
    logger.info("✅ Default system settings seeded")


async def seed_meal_schedules(db: AsyncSession, created_by_id: str) -> None:
    """Create default meal schedules if none exist."""
    from app.models.meal import MealSchedule
    from sqlalchemy import select
    from datetime import time

    result = await db.execute(select(MealSchedule))
    if result.scalars().first():
        return

    schedules = [
        MealSchedule(
            meal_type="BREAKFAST",
            start_time=time(7, 0),
            end_time=time(9, 0),
            cancel_deadline=time(6, 30),
            is_active=True,
            created_by=created_by_id,
        ),
        MealSchedule(
            meal_type="LUNCH",
            start_time=time(12, 0),
            end_time=time(14, 0),
            cancel_deadline=time(11, 30),
            is_active=True,
            created_by=created_by_id,
        ),
        MealSchedule(
            meal_type="DINNER",
            start_time=time(19, 0),
            end_time=time(21, 0),
            cancel_deadline=time(18, 30),
            is_active=True,
            created_by=created_by_id,
        ),
    ]

    for schedule in schedules:
        db.add(schedule)

    await db.commit()
    logger.info("✅ Default meal schedules seeded")


async def ensure_provost(db: AsyncSession) -> str | None:
    """Ensure the provost account exists. Returns provost ID."""
    from app.models.user import User
    from app.core.permissions import UserRole
    from sqlalchemy import select

    result = await db.execute(
        select(User).where(User.role == UserRole.PROVOST.value)
    )
    provost = result.scalars().first()

    if not provost:
        logger.warning("No provost account found. Run scripts/seed_db.py to seed test accounts.")
        return None

    return str(provost.id)


async def init_db(db: AsyncSession) -> None:
    """Run all initialization steps in order."""
    try:
        await create_tables()
        provost_id = await ensure_provost(db)
        await seed_default_settings(db)
        if provost_id:
            await seed_meal_schedules(db, provost_id)
    except Exception as exc:
        logger.error(f"Database initialization error: {exc}")
        raise
