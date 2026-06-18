"""Periodic background tasks: report generation and housekeeping."""
from __future__ import annotations

from celery import shared_task
from celery.utils.log import get_task_logger
from datetime import date, timedelta

logger = get_task_logger(__name__)


@shared_task(name="app.tasks.report_tasks.generate_daily_report")
def generate_daily_report() -> dict:
    """Generate and cache the daily report snapshot at end-of-day."""
    try:
        import asyncio

        async def _run():
            from app.db.session import AsyncSessionLocal
            from app.services.meal_service import ReportService
            from app.repositories.meal_repo import (
                MealScheduleRepository,
                StudentMealRepository,
                ExpenseRepository,
                MealRequestRepository,
            )

            yesterday = date.today() - timedelta(days=1)

            async with AsyncSessionLocal() as db:
                report_service = ReportService(
                    meal_repo=StudentMealRepository(db),
                    expense_repo=ExpenseRepository(db),
                    request_repo=MealRequestRepository(db),
                    user_repo=None,  # Not needed for basic stats
                )
                report = await report_service.generate(
                    start_date=yesterday,
                    end_date=yesterday,
                )
                logger.info(f"Daily report generated for {yesterday}: {report}")
                return {"date": str(yesterday), "status": "generated"}

        result = asyncio.get_event_loop().run_until_complete(_run())
        return result

    except Exception as exc:
        logger.error(f"Daily report generation failed: {exc}")
        return {"error": str(exc)}


@shared_task(name="app.tasks.report_tasks.cleanup_expired_tokens")
def cleanup_expired_tokens() -> dict:
    """Delete expired refresh tokens from the database."""
    try:
        import asyncio

        async def _run():
            from app.db.session import AsyncSessionLocal
            from app.repositories.user_repo import RefreshTokenRepository
            from sqlalchemy import delete
            from app.models.user import RefreshToken
            from datetime import datetime, timezone

            async with AsyncSessionLocal() as db:
                repo = RefreshTokenRepository(db)
                await repo.delete_expired()
                await db.commit()
                logger.info("Expired refresh tokens cleaned up")

        asyncio.get_event_loop().run_until_complete(_run())
        return {"status": "cleaned"}

    except Exception as exc:
        logger.error(f"Token cleanup failed: {exc}")
        return {"error": str(exc)}


@shared_task(name="app.tasks.report_tasks.generate_monthly_summary")
def generate_monthly_summary(year: int, month: int) -> dict:
    """Generate a monthly summary report for the given year/month."""
    try:
        import asyncio
        import calendar

        last_day = calendar.monthrange(year, month)[1]
        start = date(year, month, 1)
        end = date(year, month, last_day)

        async def _run():
            from app.db.session import AsyncSessionLocal
            from app.services.meal_service import ReportService
            from app.repositories.meal_repo import (
                StudentMealRepository,
                ExpenseRepository,
                MealRequestRepository,
            )

            async with AsyncSessionLocal() as db:
                report_service = ReportService(
                    meal_repo=StudentMealRepository(db),
                    expense_repo=ExpenseRepository(db),
                    request_repo=MealRequestRepository(db),
                    user_repo=None,
                )
                report = await report_service.generate(
                    start_date=start,
                    end_date=end,
                )
                return report

        result = asyncio.get_event_loop().run_until_complete(_run())
        logger.info(f"Monthly summary generated for {year}-{month:02d}")
        return {"year": year, "month": month, "status": "generated"}

    except Exception as exc:
        logger.error(f"Monthly summary generation failed: {exc}")
        return {"error": str(exc)}


@shared_task(name="app.tasks.report_tasks.archive_old_audit_logs")
def archive_old_audit_logs(days_to_keep: int = 365) -> dict:
    """Archive (soft-remove) audit log entries older than the retention period."""
    try:
        import asyncio
        from datetime import datetime, timezone

        cutoff = datetime.now(timezone.utc) - timedelta(days=days_to_keep)

        async def _run():
            from app.db.session import AsyncSessionLocal
            from sqlalchemy import delete
            from app.models.expense import AuditLog

            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    delete(AuditLog).where(AuditLog.created_at < cutoff)
                )
                await db.commit()
                return result.rowcount

        deleted = asyncio.get_event_loop().run_until_complete(_run())
        logger.info(f"Archived {deleted} audit log entries older than {days_to_keep} days")
        return {"deleted": deleted, "cutoff": cutoff.isoformat()}

    except Exception as exc:
        logger.error(f"Audit log archival failed: {exc}")
        return {"error": str(exc)}
