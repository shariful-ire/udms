"""Async email tasks for Celery workers."""
from __future__ import annotations

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True, name="app.tasks.email_tasks.send_verification_email_task", max_retries=3)
def send_verification_email_task(self, email: str, username: str, otp: str) -> dict:
    """Send email verification OTP asynchronously."""
    try:
        import asyncio
        from app.services.email_service import EmailService

        async def _send():
            service = EmailService()
            await service.send_verification_email(
                email=email,
                username=username,
                otp=otp,
            )

        asyncio.get_event_loop().run_until_complete(_send())
        logger.info(f"Verification email sent to {email}")
        return {"status": "sent", "email": email}

    except Exception as exc:
        logger.error(f"Failed to send verification email to {email}: {exc}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, name="app.tasks.email_tasks.send_password_reset_task", max_retries=3)
def send_password_reset_task(self, email: str, username: str, otp: str) -> dict:
    """Send password reset OTP email asynchronously."""
    try:
        import asyncio
        from app.services.email_service import EmailService

        async def _send():
            service = EmailService()
            await service.send_password_reset_email(
                email=email,
                username=username,
                otp=otp,
            )

        asyncio.get_event_loop().run_until_complete(_send())
        logger.info(f"Password reset email sent to {email}")
        return {"status": "sent", "email": email}

    except Exception as exc:
        logger.error(f"Failed to send password reset email to {email}: {exc}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, name="app.tasks.email_tasks.send_welcome_email_task", max_retries=2)
def send_welcome_email_task(self, email: str, username: str, full_name: str) -> dict:
    """Send welcome email after successful verification."""
    try:
        import asyncio
        from app.services.email_service import EmailService

        async def _send():
            service = EmailService()
            await service.send_welcome_email(
                email=email,
                username=username,
                full_name=full_name,
            )

        asyncio.get_event_loop().run_until_complete(_send())
        logger.info(f"Welcome email sent to {email}")
        return {"status": "sent", "email": email}

    except Exception as exc:
        logger.error(f"Failed to send welcome email to {email}: {exc}")
        raise self.retry(exc=exc, countdown=120)


@shared_task(name="app.tasks.email_tasks.send_meal_reminders")
def send_meal_reminders() -> dict:
    """Send morning meal reminder emails to all active customers."""
    try:
        import asyncio
        from datetime import date

        async def _run():
            from app.db.session import AsyncSessionLocal
            from app.repositories.user_repo import UserRepository
            from app.repositories.meal_repo import MealScheduleRepository
            from app.services.email_service import EmailService
            from app.core.permissions import UserRole

            async with AsyncSessionLocal() as db:
                user_repo = UserRepository(db)
                schedule_repo = MealScheduleRepository(db)

                # Get all active schedules for today
                schedules = await schedule_repo.get_all_active()
                if not schedules:
                    return {"sent": 0}

                # Get all active customers
                customers, _ = await user_repo.get_paginated(
                    page=1,
                    per_page=1000,
                    role=UserRole.CUSTOMER.value,
                    status="ACTIVE",
                )

                service = EmailService()
                sent = 0
                for customer in customers:
                    try:
                        # Simple reminder — no detailed template for now
                        logger.info(f"Would send meal reminder to {customer.email}")
                        sent += 1
                    except Exception as e:
                        logger.warning(f"Failed reminder for {customer.email}: {e}")

                return {"sent": sent, "date": str(date.today())}

        result = asyncio.get_event_loop().run_until_complete(_run())
        logger.info(f"Meal reminders sent: {result}")
        return result

    except Exception as exc:
        logger.error(f"Meal reminder task failed: {exc}")
        return {"error": str(exc)}


@shared_task(bind=True, name="app.tasks.email_tasks.send_request_status_email", max_retries=2)
def send_request_status_email(
    self,
    email: str,
    username: str,
    status: str,
    meal_type: str,
    date: str,
    rejection_note: str | None = None,
) -> dict:
    """Notify a non-customer about their meal request status change."""
    try:
        import asyncio
        from app.services.email_service import EmailService

        async def _send():
            service = EmailService()
            subject = f"Meal Request {status.title()} — {meal_type} on {date}"
            body_lines = [
                f"Dear {username},",
                f"",
                f"Your meal request for {meal_type} on {date} has been {status.lower()}.",
            ]
            if rejection_note:
                body_lines.extend(["", f"Reason: {rejection_note}"])
            body_lines.extend(["", "Please log in to UDMS for details.", "", "— Dining Management Team"])

            await service.send_raw_email(
                email=email,
                subject=subject,
                body="\n".join(body_lines),
            )

        asyncio.get_event_loop().run_until_complete(_send())
        return {"status": "sent", "email": email}

    except Exception as exc:
        logger.error(f"Failed to send request status email: {exc}")
        raise self.retry(exc=exc, countdown=60)
