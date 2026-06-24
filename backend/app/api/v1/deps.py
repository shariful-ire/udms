from typing import Optional

import redis.asyncio as aioredis
from fastapi import Cookie, Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    UnauthenticatedException,
    InvalidTokenException,
    TokenExpiredException,
)
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repo import UserRepository

# ─── HTTP Bearer ──────────────────────────────────────────────────────────────
_bearer = HTTPBearer(auto_error=False)

# ─── Redis Client ─────────────────────────────────────────────────────────────
_redis_pool: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _redis_pool
    if _redis_pool is None:
        try:
            _redis_pool = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=False,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
            )
        except Exception:
            logger.warning("Could not create Redis connection pool")
            _redis_pool = aioredis.from_url("redis://localhost:6379/0")
    return _redis_pool


# ─── Current User Extraction ──────────────────────────────────────────────────
async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extract and validate current user from Authorization: Bearer <token>.
    Also attempts to read from X-Access-Token header as fallback.
    """
    token: Optional[str] = None

    if credentials and credentials.credentials:
        token = credentials.credentials
    else:
        # Fallback: check X-Access-Token header (for Next.js API proxy usage)
        token = request.headers.get("X-Access-Token")

    if not token:
        raise UnauthenticatedException()

    try:
        payload = decode_access_token(token)
    except (InvalidTokenException, TokenExpiredException):
        raise

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenException("Token payload missing subject")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise InvalidTokenException("User no longer exists")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensures user is active (not suspended or inactive)."""
    from app.core.exceptions import InactiveAccountException, SuspendedAccountException
    if current_user.status == "SUSPENDED":
        raise SuspendedAccountException()
    if current_user.status == "INACTIVE":
        raise InactiveAccountException()
    return current_user


async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Like get_current_user but returns None instead of raising if unauthenticated."""
    try:
        return await get_current_user(request, credentials, db)
    except Exception:
        return None


def get_client_ip(request: Request) -> str:
    """Extract real client IP from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    return request.headers.get("User-Agent", "")[:500]
