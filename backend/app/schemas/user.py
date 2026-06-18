from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    student_id: str
    department: Optional[str] = None
    batch: Optional[str] = None
    hall_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: str = "NON_CUSTOMER"


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=150)
    department: Optional[str] = Field(None, max_length=100)
    batch: Optional[str] = Field(None, max_length=20)
    hall_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class UserAdminUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    batch: Optional[str] = None
    hall_name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    student_id: str
    username: str
    full_name: str
    email: str
    role: str
    department: Optional[str] = None
    batch: Optional[str] = None
    hall_name: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None
    status: str
    email_verified: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserSummary(BaseModel):
    """Lightweight user representation for lists and dropdowns."""
    id: str
    username: str
    full_name: str
    email: str
    role: str
    status: str
    student_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        import re
        errors = []
        if not re.search(r"[A-Z]", v):
            errors.append("uppercase letter")
        if not re.search(r"[a-z]", v):
            errors.append("lowercase letter")
        if not re.search(r"\d", v):
            errors.append("digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=]", v):
            errors.append("special character")
        if errors:
            raise ValueError(f"Password must contain: {', '.join(errors)}")
        return v


class UserStatsResponse(BaseModel):
    total_users: int
    total_customers: int
    total_non_customers: int
    total_managers: int
    active_users: int
    inactive_users: int
    suspended_users: int
