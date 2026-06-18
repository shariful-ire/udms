from pathlib import Path
from typing import List, Optional

import redis.asyncio as aioredis
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jinja2 import Environment, FileSystemLoader
from loguru import logger

from app.core.config import settings

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "email"

_jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=True,
)

_mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS,
    VALIDATE_CERTS=settings.MAIL_VALIDATE_CERTS,
)

_fast_mail = FastMail(_mail_config)


class EmailService:
    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        self.redis = redis_client

    def _render(self, template_name: str, context: dict) -> str:
        template = _jinja_env.get_template(template_name)
        return template.render(**context)

    async def _send(self, to: str, subject: str, html_body: str) -> bool:
        try:
            message = MessageSchema(
                subject=subject,
                recipients=[to],
                body=html_body,
                subtype=MessageType.html,
            )
            await _fast_mail.send_message(message)
            logger.info(f"Email sent to {to}: {subject}")
            return True
        except Exception as exc:
            logger.error(f"Failed to send email to {to}: {exc}")
            return False

    async def send_verification_email(
        self, to_email: str, full_name: str, otp: str
    ) -> bool:
        html = self._render(
            "verification.html",
            {
                "full_name": full_name,
                "otp": otp,
                "otp_expiry_minutes": settings.OTP_EXPIRE_MINUTES,
                "app_name": settings.APP_NAME,
                "frontend_url": settings.FRONTEND_URL,
            },
        )
        return await self._send(
            to=to_email,
            subject=f"Verify your {settings.APP_NAME} account",
            html_body=html,
        )

    async def send_password_reset_email(
        self, to_email: str, full_name: str, otp: str
    ) -> bool:
        html = self._render(
            "password_reset.html",
            {
                "full_name": full_name,
                "otp": otp,
                "otp_expiry_minutes": settings.PASSWORD_RESET_OTP_EXPIRE_MINUTES,
                "app_name": settings.APP_NAME,
                "frontend_url": settings.FRONTEND_URL,
            },
        )
        return await self._send(
            to=to_email,
            subject=f"Reset your {settings.APP_NAME} password",
            html_body=html,
        )

    async def send_raw_email(self, email: str, subject: str, body: str) -> bool:
        """Send a plain-text email (rendered as HTML pre-formatted)."""
        html_body = f"<pre style='font-family:sans-serif;white-space:pre-wrap'>{body}</pre>"
        return await self._send(to=email, subject=subject, html_body=html_body)

    async def send_welcome_email(self, to_email: str, full_name: str) -> bool:
        html = self._render(
            "welcome.html",
            {
                "full_name": full_name,
                "app_name": settings.APP_NAME,
                "frontend_url": settings.FRONTEND_URL,
                "login_url": f"{settings.FRONTEND_URL}/login",
            },
        )
        return await self._send(
            to=to_email,
            subject=f"Welcome to {settings.APP_NAME}!",
            html_body=html,
        )
