"""Shared Pydantic v2 validators used across multiple schemas."""
from __future__ import annotations

import re
from typing import Any


# ─── Password ──────────────────────────────────────────────────────────────────

_PASSWORD_RE = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{}|;':\",./<>?]).{8,128}$"
)

_COMMON_PASSWORDS = {
    "Password1!",
    "Password123!",
    "Admin123!",
    "Qwerty123!",
    "Welcome1!",
}


def validate_password(value: str) -> str:
    """Enforce password policy: 8+ chars, uppercase, lowercase, digit, special char."""
    if not value:
        raise ValueError("Password is required")
    if len(value) < 8:
        raise ValueError("Password must be at least 8 characters")
    if len(value) > 128:
        raise ValueError("Password must be at most 128 characters")
    if not _PASSWORD_RE.match(value):
        raise ValueError(
            "Password must contain at least one uppercase letter, one lowercase letter, "
            "one digit, and one special character"
        )
    if value in _COMMON_PASSWORDS:
        raise ValueError("Password is too common — please choose a stronger password")
    return value


# ─── Username ──────────────────────────────────────────────────────────────────

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,50}$")


def validate_username(value: str) -> str:
    """Allow only alphanumeric + underscore, 3–50 chars."""
    if not value:
        raise ValueError("Username is required")
    value = value.strip().lower()
    if not _USERNAME_RE.match(value):
        raise ValueError(
            "Username must be 3–50 characters and contain only letters, numbers, and underscores"
        )
    reserved = {"admin", "root", "system", "null", "undefined", "api", "provost"}
    if value in reserved:
        raise ValueError(f"Username '{value}' is reserved and cannot be used")
    return value


# ─── Student ID ────────────────────────────────────────────────────────────────

_STUDENT_ID_RE = re.compile(r"^[A-Z0-9\-]{4,20}$")


def validate_student_id(value: str) -> str:
    """Student ID: 4–20 uppercase alphanumeric (and dashes)."""
    if not value:
        raise ValueError("Student ID is required")
    value = value.strip().upper()
    if not _STUDENT_ID_RE.match(value):
        raise ValueError(
            "Student ID must be 4–20 characters (letters, numbers, and dashes only)"
        )
    return value


# ─── Phone ─────────────────────────────────────────────────────────────────────

_PHONE_RE = re.compile(r"^\+?[0-9\s\-]{7,20}$")


def validate_phone(value: str | None) -> str | None:
    """Optional phone: international format, 7–20 digits/spaces/dashes."""
    if not value:
        return value
    value = value.strip()
    if not _PHONE_RE.match(value):
        raise ValueError("Phone number format is invalid")
    return value


# ─── OTP ───────────────────────────────────────────────────────────────────────

def validate_otp(value: str) -> str:
    """OTP must be exactly 6 numeric digits."""
    if not value or not value.isdigit() or len(value) != 6:
        raise ValueError("OTP must be exactly 6 digits")
    return value


# ─── Amount ────────────────────────────────────────────────────────────────────

def validate_positive_amount(value: Any) -> Any:
    """Decimal/float value must be positive."""
    if value is not None and float(value) <= 0:
        raise ValueError("Amount must be greater than zero")
    return value


# ─── Date range ────────────────────────────────────────────────────────────────

def validate_date_range(start, end) -> None:
    """Raise if start > end."""
    if start and end and start > end:
        raise ValueError("Start date must not be after end date")
