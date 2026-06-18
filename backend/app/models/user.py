import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    student_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum("PROVOST", "DINING_MANAGER", "CUSTOMER", "NON_CUSTOMER", name="user_role"),
        nullable=False,
        default="NON_CUSTOMER",
        index=True,
    )
    department: Mapped[Optional[str]] = mapped_column(String(100))
    batch: Mapped[Optional[str]] = mapped_column(String(20))
    hall_name: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    profile_image: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(
        Enum("ACTIVE", "INACTIVE", "SUSPENDED", name="user_status"),
        nullable=False,
        default="INACTIVE",
        index=True,
    )
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    failed_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    student_meals: Mapped[List["StudentMeal"]] = relationship(
        "StudentMeal", back_populates="user", cascade="all, delete-orphan"
    )
    meal_requests: Mapped[List["MealRequest"]] = relationship(
        "MealRequest", back_populates="user", foreign_keys="MealRequest.user_id"
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment", back_populates="user"
    )
    expenses_created: Mapped[List["Expense"]] = relationship(
        "Expense", back_populates="created_by_user", foreign_keys="Expense.created_by"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username} role={self.role}>"

    @property
    def is_active(self) -> bool:
        return self.status == "ACTIVE"

    @property
    def is_suspended(self) -> bool:
        return self.status == "SUSPENDED"

    @property
    def is_inactive(self) -> bool:
        return self.status == "INACTIVE"


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

    def __repr__(self) -> str:
        return f"<RefreshToken id={self.id} user_id={self.user_id}>"
