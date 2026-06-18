"""Pagination helpers — offset-based with metadata."""
from __future__ import annotations

from math import ceil
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PageMeta(BaseModel):
    """Pagination metadata returned in every list response."""
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


def build_meta(page: int, per_page: int, total: int) -> PageMeta:
    """Construct pagination metadata from raw counts."""
    total_pages = ceil(total / per_page) if per_page > 0 else 1
    return PageMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=max(total_pages, 1),
        has_next=page < total_pages,
        has_prev=page > 1,
    )


def get_offset(page: int, per_page: int) -> int:
    """Convert 1-indexed page number to SQL OFFSET."""
    return (max(page, 1) - 1) * per_page


def paginated_response(
    data: list[Any],
    page: int,
    per_page: int,
    total: int,
    message: str = "Data retrieved successfully",
) -> dict:
    """Wrap a list result in the standard paginated API response envelope."""
    meta = build_meta(page=page, per_page=per_page, total=total)
    return {
        "success": True,
        "message": message,
        "data": data,
        "meta": meta.model_dump(),
    }


def single_response(
    data: Any,
    message: str = "Data retrieved successfully",
) -> dict:
    """Wrap a single object in the standard API response envelope."""
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def ok_response(message: str = "Operation completed successfully", data: Any = None) -> dict:
    """Success response with optional data payload."""
    resp: dict = {"success": True, "message": message}
    if data is not None:
        resp["data"] = data
    return resp


def error_response(
    message: str,
    error_code: str = "ERROR",
    errors: list[dict] | None = None,
) -> dict:
    """Standard error response envelope."""
    resp: dict = {"success": False, "message": message, "error_code": error_code}
    if errors:
        resp["errors"] = errors
    return resp
