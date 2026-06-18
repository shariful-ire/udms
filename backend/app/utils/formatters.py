"""Response formatting helpers used throughout the API layer."""
from __future__ import annotations

from decimal import Decimal
from typing import Any


def format_currency(value: Decimal | float | None, symbol: str = "৳") -> str:
    """Format a decimal value as a human-readable currency string."""
    if value is None:
        return f"{symbol}0.00"
    return f"{symbol}{float(value):,.2f}"


def format_meal_type(meal_type: str) -> str:
    """Capitalize and format meal type enum value."""
    return meal_type.replace("_", " ").title()


def format_role(role: str) -> str:
    """Format role enum into human-readable string."""
    mapping = {
        "PROVOST": "Provost",
        "DINING_MANAGER": "Dining Manager",
        "CUSTOMER": "Customer",
        "NON_CUSTOMER": "Student",
    }
    return mapping.get(role, role.replace("_", " ").title())


def format_status(status: str) -> str:
    """Format status enum into human-readable string."""
    mapping = {
        "ACTIVE": "Active",
        "INACTIVE": "Inactive",
        "SUSPENDED": "Suspended",
        "PENDING_PAYMENT": "Pending Payment",
        "PENDING_APPROVAL": "Pending Approval",
        "APPROVED": "Approved",
        "REJECTED": "Rejected",
        "CANCELLED": "Cancelled",
        "COMPLETED": "Completed",
        "FAILED": "Failed",
        "REFUNDED": "Refunded",
    }
    return mapping.get(status, status.replace("_", " ").title())


def truncate(text: str | None, max_length: int = 100, suffix: str = "…") -> str | None:
    """Truncate long text with ellipsis."""
    if not text:
        return text
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def mask_email(email: str) -> str:
    """Return partially masked email: j***@example.com."""
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    masked_local = local[0] + "***" if len(local) > 1 else "***"
    return f"{masked_local}@{domain}"


def success_response(message: str, data: Any = None, meta: dict | None = None) -> dict:
    """Standard success response envelope."""
    resp: dict = {"success": True, "message": message}
    if data is not None:
        resp["data"] = data
    if meta is not None:
        resp["meta"] = meta
    return resp


def error_response(
    message: str,
    error_code: str = "ERROR",
    errors: list[dict] | None = None,
    status_code: int = 400,
) -> dict:
    """Standard error response envelope."""
    resp: dict = {"success": False, "message": message, "error_code": error_code}
    if errors:
        resp["errors"] = errors
    return resp
