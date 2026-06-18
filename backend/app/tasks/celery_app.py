"""Celery application factory and configuration."""
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "udms",
    broker=settings.CELERY_BROKER,
    backend=settings.CELERY_BACKEND,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.report_tasks",
    ],
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Task behavior
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    # Result expiry
    result_expires=3600,
    # Worker concurrency
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    # Retry
    task_default_retry_delay=60,
    task_max_retries=3,
    # Rate limits
    task_default_rate_limit="100/m",
    # Beat schedule for periodic tasks
    beat_schedule={
        "generate-daily-report": {
            "task": "app.tasks.report_tasks.generate_daily_report",
            "schedule": crontab(hour=23, minute=55),
            "options": {"expires": 3600},
        },
        "cleanup-expired-tokens": {
            "task": "app.tasks.report_tasks.cleanup_expired_tokens",
            "schedule": crontab(hour=2, minute=0),
            "options": {"expires": 3600},
        },
        "send-meal-reminders": {
            "task": "app.tasks.email_tasks.send_meal_reminders",
            "schedule": crontab(hour=6, minute=30),
            "options": {"expires": 1800},
        },
    },
)
