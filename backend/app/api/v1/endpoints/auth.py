from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, Request, Response
from fastapi.responses import JSONResponse
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import (
    get_client_ip,
    get_current_active_user,
    get_db,
    get_redis,
    get_user_agent,
)
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
    VerifyOTPRequest,
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)

REFRESH_COOKIE = "refresh_token"
COOKIE_MAX_AGE = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400


def _set_refresh_cookie(response: Response, token: str, expires: datetime) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="strict",
        max_age=COOKIE_MAX_AGE,
        path="/api/v1/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=REFRESH_COOKIE, path="/api/v1/auth")


@router.post("/register", status_code=201)
async def register(
    data: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """Register a new student account."""
    service = AuthService(db, redis)
    result = await service.register(data, request)
    return {"success": True, "message": result["message"], "data": {"email": result["email"]}}


@router.post("/verify-email")
async def verify_email(
    data: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """Verify email with OTP."""
    service = AuthService(db, redis)
    result = await service.verify_email(data.email, data.otp)
    return {"success": True, **result}


@router.post("/resend-verification")
async def resend_verification(
    data: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """Resend email verification OTP (60s cooldown)."""
    service = AuthService(db, redis)
    result = await service.resend_verification(data.email)
    return {"success": True, **result}


@router.post("/login")
async def login(
    data: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """Authenticate and receive access + refresh tokens."""
    service = AuthService(db, redis)
    token_response, raw_refresh, refresh_expiry = await service.login(data, request)
    _set_refresh_cookie(response, raw_refresh, refresh_expiry)

    # Get user details
    from app.repositories.user_repo import UserRepository
    user_repo = UserRepository(db)
    from app.core.security import decode_access_token
    payload = decode_access_token(token_response.access_token)
    user = await user_repo.get_by_id(payload["sub"])

    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "access_token": token_response.access_token,
            "token_type": "bearer",
            "expires_in": token_response.expires_in,
            "user": UserResponse.model_validate(user),
        },
    }


@router.post("/refresh")
async def refresh_tokens(
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    refresh_token: Optional[str] = Cookie(default=None, alias=REFRESH_COOKIE),
    body: Optional[RefreshRequest] = None,
):
    """Rotate access + refresh tokens."""
    raw_token = refresh_token or (body.refresh_token if body else None)
    if not raw_token:
        from app.core.exceptions import UnauthenticatedException
        raise UnauthenticatedException("No refresh token provided")

    service = AuthService(db, redis)
    token_response, new_refresh, new_expiry = await service.refresh_tokens(raw_token)
    _set_refresh_cookie(response, new_refresh, new_expiry)

    return {
        "success": True,
        "data": {
            "access_token": token_response.access_token,
            "expires_in": token_response.expires_in,
        },
    }


@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    refresh_token: Optional[str] = Cookie(default=None, alias=REFRESH_COOKIE),
):
    """Invalidate tokens and clear cookie."""
    service = AuthService(db, redis)
    await service.logout(refresh_token, current_user.id)
    _clear_refresh_cookie(response)
    return {"success": True, "message": "Logged out successfully"}


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """Send password reset OTP (prevents email enumeration)."""
    service = AuthService(db, redis)
    result = await service.forgot_password(data.email)
    return {"success": True, **result}


@router.post("/verify-otp")
async def verify_reset_otp(
    data: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """Validate password reset OTP before allowing password change."""
    service = AuthService(db, redis)
    result = await service.verify_reset_otp(data.email, data.otp)
    return {"success": True, **result}


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """Reset password using verified OTP."""
    service = AuthService(db, redis)
    result = await service.reset_password(data.email, data.otp, data.new_password)
    return {"success": True, **result}


@router.get("/me", response_model=dict)
async def get_me(
    current_user: User = Depends(get_current_active_user),
):
    """Return current user's profile and permissions."""
    from app.core.permissions import ROLE_PERMISSIONS, UserRole, get_effective_permissions
    role = UserRole(current_user.role)
    perms = [p.value for p in get_effective_permissions(role)]

    return {
        "success": True,
        "data": {
            "user": UserResponse.model_validate(current_user),
            "permissions": perms,
        },
    }
