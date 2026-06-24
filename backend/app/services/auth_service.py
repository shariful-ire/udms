from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

import redis.asyncio as aioredis
from fastapi import Request
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    AccountLockedOutException,
    ConflictException,
    InactiveAccountException,
    InvalidCredentialsException,
    OTPCooldownException,
    OTPExpiredException,
    OTPInvalidException,
    SuspendedAccountException,
    InvalidTokenException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    generate_otp,
    hash_password,
    hash_token,
    needs_rehash,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repo import RefreshTokenRepository, UserRepository
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse
from app.services.email_service import EmailService


class AuthService:
    def __init__(self, db: AsyncSession, redis_client: aioredis.Redis):
        self.db = db
        self.redis = redis_client
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)
        self.email_service = EmailService(redis_client)

    # ─── Redis Key Helpers ────────────────────────────────────────────────────
    def _otp_key(self, email: str, purpose: str) -> str:
        return f"otp:{purpose}:{email.lower()}"

    def _cooldown_key(self, email: str, purpose: str) -> str:
        return f"otp_cooldown:{purpose}:{email.lower()}"

    def _lockout_key(self, identifier: str) -> str:
        return f"lockout:{identifier.lower()}"

    # ─── Registration ─────────────────────────────────────────────────────────
    async def register(self, data: RegisterRequest, request: Request = None) -> dict:
        # Check uniqueness
        if await self.user_repo.get_by_username(data.username):
            raise ConflictException("Username already taken")
        if await self.user_repo.get_by_email(data.email):
            raise ConflictException("Email address already registered")
        if await self.user_repo.get_by_student_id(data.student_id):
            raise ConflictException("Student ID already registered")

        # Try OTP flow via Redis; if Redis is down, auto-activate the user
        try:
            await self.redis.ping()
            redis_available = True
        except Exception:
            redis_available = False
            logger.warning("Redis unavailable — user will be auto-activated without email verification")

        # Create user
        user = await self.user_repo.create({
            "username": data.username.lower(),
            "email": data.email.lower(),
            "full_name": data.full_name,
            "password_hash": hash_password(data.password),
            "student_id": data.student_id,
            "department": data.department,
            "batch": data.batch,
            "hall_name": data.hall_name,
            "phone": data.phone,
            "status": "ACTIVE" if not redis_available else "INACTIVE",
            "email_verified": not redis_available,
            "role": "NON_CUSTOMER",
        })

        if redis_available:
            # Generate & store OTP
            otp = generate_otp()
            otp_key = self._otp_key(data.email, "verify")
            await self.redis.setex(
                otp_key,
                settings.OTP_EXPIRE_MINUTES * 60,
                otp,
            )

            # Send verification email
            await self.email_service.send_verification_email(
                to_email=data.email,
                full_name=data.full_name,
                otp=otp,
            )

            logger.info(f"New user registered: {data.username} ({data.email})")
            return {"message": "Registration successful. Please check your email for the verification code.", "email": data.email}
        else:
            logger.info(f"New user registered & auto-activated: {data.username} ({data.email})")
            return {"message": "Registration successful. Your account is now active. You can log in.", "email": data.email}

    # ─── Email Verification ───────────────────────────────────────────────────
    async def verify_email(self, email: str, otp: str) -> dict:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise OTPInvalidException()

        if user.email_verified and user.status == "ACTIVE":
            return {"message": "Email already verified."}

        otp_key = self._otp_key(email, "verify")
        stored_otp = await self.redis.get(otp_key)
        if not stored_otp:
            raise OTPExpiredException()

        stored_str = stored_otp.decode() if isinstance(stored_otp, bytes) else stored_otp
        if stored_str != otp:
            raise OTPInvalidException()

        # Activate account
        await self.user_repo.update(user, {
            "email_verified": True,
            "status": "ACTIVE",
        })
        await self.redis.delete(otp_key)

        logger.info(f"Email verified for user: {user.username}")
        return {"message": "Email verified successfully. You can now log in."}

    async def resend_verification(self, email: str) -> dict:
        user = await self.user_repo.get_by_email(email)
        # Always return success to prevent email enumeration
        if not user or (user.email_verified and user.status == "ACTIVE"):
            return {"message": "If that email exists, a new code will be sent."}

        # Cooldown check
        cooldown_key = self._cooldown_key(email, "verify")
        if await self.redis.exists(cooldown_key):
            ttl = await self.redis.ttl(cooldown_key)
            raise OTPCooldownException(seconds=ttl)

        otp = generate_otp()
        otp_key = self._otp_key(email, "verify")
        await self.redis.setex(otp_key, settings.OTP_EXPIRE_MINUTES * 60, otp)
        await self.redis.setex(cooldown_key, settings.OTP_RESEND_COOLDOWN_SECONDS, "1")

        await self.email_service.send_verification_email(
            to_email=email,
            full_name=user.full_name,
            otp=otp,
        )
        return {"message": "If that email exists, a new code will be sent."}

    # ─── Login ────────────────────────────────────────────────────────────────
    async def login(
        self, data: LoginRequest, request: Request = None
    ) -> Tuple[TokenResponse, str, datetime]:
        user = await self.user_repo.get_by_identifier(data.identifier)

        if not user:
            raise InvalidCredentialsException()

        # Status checks
        if user.status == "SUSPENDED":
            raise SuspendedAccountException()
        if user.status == "INACTIVE":
            raise InactiveAccountException()

        # Lockout check
        if user.locked_until and user.locked_until > datetime.utcnow():
            remaining = int((user.locked_until - datetime.utcnow()).total_seconds() / 60)
            raise AccountLockedOutException(minutes=max(remaining, 1))

        # Password verification
        if not verify_password(data.password, user.password_hash):
            attempts = await self.user_repo.increment_failed_attempts(user.id)
            if attempts >= settings.MAX_LOGIN_ATTEMPTS:
                locked_until = datetime.utcnow() + timedelta(
                    minutes=settings.ACCOUNT_LOCKOUT_MINUTES
                )
                await self.user_repo.lock_account(user.id, locked_until)
                raise AccountLockedOutException(minutes=settings.ACCOUNT_LOCKOUT_MINUTES)
            raise InvalidCredentialsException()

        # Reset failed attempts & update last login
        await self.user_repo.reset_failed_attempts(user.id)
        await self.user_repo.update_last_login(user.id)

        # Optionally rehash password if using bcrypt
        if needs_rehash(user.password_hash):
            await self.user_repo.update(user, {"password_hash": hash_password(data.password)})

        # Issue tokens
        access_token = create_access_token(
            subject=user.id,
            username=user.username,
            role=user.role,
            email=user.email,
        )
        raw_refresh, refresh_hash, refresh_expiry = create_refresh_token(user.id)

        # Delete old refresh tokens; store new one
        await self.token_repo.delete_by_user_id(user.id)
        await self.token_repo.create({
            "user_id": user.id,
            "token_hash": refresh_hash,
            "expires_at": refresh_expiry,
        })

        token_response = TokenResponse(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        logger.info(f"Login success: {user.username}")
        return token_response, raw_refresh, refresh_expiry

    # ─── Token Refresh ────────────────────────────────────────────────────────
    async def refresh_tokens(
        self, raw_refresh_token: str
    ) -> Tuple[TokenResponse, str, datetime]:
        payload = decode_refresh_token(raw_refresh_token)
        user_id = payload.get("sub")

        # Verify token hash exists in DB
        token_hash = hash_token(raw_refresh_token)
        db_token = await self.token_repo.get_by_hash(token_hash)
        if not db_token or db_token.user_id != user_id:
            raise InvalidTokenException("Refresh token not recognized")

        if db_token.expires_at < datetime.utcnow():
            await self.token_repo.delete(db_token)
            raise InvalidTokenException("Refresh token has expired")

        user = await self.user_repo.get_by_id(user_id)
        if not user or user.status != "ACTIVE":
            raise InvalidTokenException("User account is not active")

        # Rotate tokens
        await self.token_repo.delete(db_token)
        access_token = create_access_token(
            subject=user.id,
            username=user.username,
            role=user.role,
            email=user.email,
        )
        raw_new_refresh, new_hash, new_expiry = create_refresh_token(user.id)
        await self.token_repo.create({
            "user_id": user.id,
            "token_hash": new_hash,
            "expires_at": new_expiry,
        })

        return (
            TokenResponse(
                access_token=access_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            ),
            raw_new_refresh,
            new_expiry,
        )

    # ─── Logout ───────────────────────────────────────────────────────────────
    async def logout(self, raw_refresh_token: Optional[str], user_id: str) -> dict:
        if raw_refresh_token:
            token_hash = hash_token(raw_refresh_token)
            db_token = await self.token_repo.get_by_hash(token_hash)
            if db_token:
                await self.token_repo.delete(db_token)
        else:
            # Invalidate all sessions for this user
            await self.token_repo.delete_by_user_id(user_id)

        return {"message": "Logged out successfully"}

    # ─── Forgot Password ──────────────────────────────────────────────────────
    async def forgot_password(self, email: str) -> dict:
        # Always return success to prevent email enumeration
        user = await self.user_repo.get_by_email(email)
        response = {"message": "If that email exists in our system, a reset code has been sent."}

        if not user:
            return response

        # Cooldown
        cooldown_key = self._cooldown_key(email, "reset")
        if await self.redis.exists(cooldown_key):
            return response  # Silently ignore to prevent enumeration

        otp = generate_otp()
        otp_key = self._otp_key(email, "reset")
        await self.redis.setex(otp_key, settings.PASSWORD_RESET_OTP_EXPIRE_MINUTES * 60, otp)
        await self.redis.setex(cooldown_key, settings.OTP_RESEND_COOLDOWN_SECONDS, "1")

        await self.email_service.send_password_reset_email(
            to_email=email,
            full_name=user.full_name,
            otp=otp,
        )
        return response

    async def verify_reset_otp(self, email: str, otp: str) -> dict:
        otp_key = self._otp_key(email, "reset")
        stored_otp = await self.redis.get(otp_key)
        if not stored_otp:
            raise OTPExpiredException()

        stored_str = stored_otp.decode() if isinstance(stored_otp, bytes) else stored_otp
        if stored_str != otp:
            raise OTPInvalidException()

        return {"message": "OTP verified. You may now reset your password.", "valid": True}

    async def reset_password(self, email: str, otp: str, new_password: str) -> dict:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise OTPInvalidException()

        otp_key = self._otp_key(email, "reset")
        stored_otp = await self.redis.get(otp_key)
        if not stored_otp:
            raise OTPExpiredException()

        stored_str = stored_otp.decode() if isinstance(stored_otp, bytes) else stored_otp
        if stored_str != otp:
            raise OTPInvalidException()

        # Update password & invalidate all sessions
        await self.user_repo.update(user, {"password_hash": hash_password(new_password)})
        await self.token_repo.delete_by_user_id(user.id)
        await self.redis.delete(otp_key)

        logger.info(f"Password reset for: {user.username}")
        return {"message": "Password reset successfully. Please log in with your new password."}
