from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import secrets
import hashlib
import hmac

from jose import JWTError, jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
import bcrypt

from app.core.config import settings
from app.core.exceptions import (
    InvalidCredentialsException,
    TokenExpiredException,
    InvalidTokenException,
)


# ─── Argon2 Password Hasher ─────────────────────────────────────────────────
_argon2_hasher = PasswordHasher(
    time_cost=settings.ARGON2_TIME_COST,
    memory_cost=settings.ARGON2_MEMORY_COST,
    parallelism=settings.ARGON2_PARALLELISM,
    hash_len=settings.ARGON2_HASH_LEN,
    salt_len=settings.ARGON2_SALT_LEN,
)


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using Argon2id."""
    return _argon2_hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against an Argon2 or bcrypt hash."""
    # Detect hash type
    if hashed_password.startswith("$argon2"):
        try:
            return _argon2_hasher.verify(hashed_password, plain_password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False
    elif hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
        # bcrypt fallback for legacy passwords
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except Exception:
            return False
    return False


def needs_rehash(hashed_password: str) -> bool:
    """Check if a password hash needs to be upgraded to Argon2."""
    if not hashed_password.startswith("$argon2"):
        return True
    try:
        return _argon2_hasher.check_needs_rehash(hashed_password)
    except Exception:
        return False


# ─── JWT Token Generation ────────────────────────────────────────────────────
def create_access_token(
    subject: str,
    username: str,
    role: str,
    email: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generate a signed JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    payload = {
        "sub": str(subject),
        "username": username,
        "role": role,
        "email": email,
        "iat": datetime.now(timezone.utc),
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> Tuple[str, str, datetime]:
    """
    Generate a refresh token.
    Returns: (raw_token, token_hash, expiry_datetime)
    """
    expire = datetime.utcnow() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(subject),
        "iat": datetime.now(timezone.utc),
        "exp": expire,
        "type": "refresh",
        "jti": secrets.token_urlsafe(32),  # unique ID per token
    }
    raw_token = jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    token_hash = hash_token(raw_token)
    return raw_token, token_hash, expire


def hash_token(token: str) -> str:
    """One-way hash for storing refresh tokens in DB."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "access":
            raise InvalidTokenException("Not an access token")
        return payload
    except JWTError as exc:
        if "expired" in str(exc).lower():
            raise TokenExpiredException()
        raise InvalidTokenException(str(exc))


def decode_refresh_token(token: str) -> dict:
    """Decode and validate a JWT refresh token."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise InvalidTokenException("Not a refresh token")
        return payload
    except JWTError as exc:
        if "expired" in str(exc).lower():
            raise TokenExpiredException("Refresh token has expired")
        raise InvalidTokenException(str(exc))


# ─── OTP Generation ──────────────────────────────────────────────────────────
def generate_otp(length: int = 6) -> str:
    """Generate a cryptographically secure numeric OTP."""
    import random as _random
    import os

    # Use os.urandom for cryptographic randomness
    rand = _random.SystemRandom()
    return "".join([str(rand.randint(0, 9)) for _ in range(length)])


# ─── CSRF Token ──────────────────────────────────────────────────────────────
def generate_csrf_token() -> str:
    """Generate a URL-safe CSRF token."""
    return secrets.token_urlsafe(32)


def verify_csrf_token(provided: str, expected: str) -> bool:
    """Constant-time comparison to prevent timing attacks."""
    return hmac.compare_digest(provided.encode(), expected.encode())
