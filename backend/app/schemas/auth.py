import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


# ─── Auth Schemas ─────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=150)
    student_id: str = Field(..., min_length=3, max_length=20)
    department: Optional[str] = Field(None, max_length=100)
    batch: Optional[str] = Field(None, max_length=20)
    hall_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        errors = []
        if not re.search(r"[A-Z]", v):
            errors.append("at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            errors.append("at least one lowercase letter")
        if not re.search(r"\d", v):
            errors.append("at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'/`~]", v):
            errors.append("at least one special character")
        if errors:
            raise ValueError(f"Password must contain: {', '.join(errors)}")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        return v.lower().strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.lower().strip()


class LoginRequest(BaseModel):
    identifier: str = Field(..., description="Username or email address")
    password: str = Field(..., min_length=1)


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        errors = []
        if not re.search(r"[A-Z]", v):
            errors.append("at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            errors.append("at least one lowercase letter")
        if not re.search(r"\d", v):
            errors.append("at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'/`~]", v):
            errors.append("at least one special character")
        if errors:
            raise ValueError(f"Password must contain: {', '.join(errors)}")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    """Used when refresh token is in body (non-cookie flow)."""
    refresh_token: Optional[str] = None
