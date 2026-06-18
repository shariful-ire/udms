from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None
    meta: Optional[PaginationMeta] = None

    @classmethod
    def ok(cls, data: T = None, message: str = "Operation completed successfully", meta: PaginationMeta = None):
        return cls(success=True, message=message, data=data, meta=meta)

    @classmethod
    def error(cls, message: str, data: Any = None):
        return cls(success=False, message=message, data=data)


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    errors: List[ErrorDetail] = []
    error_code: Optional[str] = None


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


def paginate(page: int, per_page: int, total: int) -> PaginationMeta:
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    return PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
