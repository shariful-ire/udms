import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BIGINT,
    JSON,
    BigInteger,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(
        Enum(
            "FOOD_PURCHASE",
            "UTILITIES",
            "SALARY",
            "EQUIPMENT",
            "MAINTENANCE",
            "MISCELLANEOUS",
            name="expense_category",
        ),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    updated_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    created_by_user: Mapped["User"] = relationship(
        "User", back_populates="expenses_created", foreign_keys=[created_by]
    )

    def __repr__(self) -> str:
        return f"<Expense {self.name} {self.amount}>"


class MealRequest(Base):
    __tablename__ = "meal_requests"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    meal_type: Mapped[str] = mapped_column(
        Enum("BREAKFAST", "LUNCH", "DINNER", name="meal_type_request"),
        nullable=False,
    )
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(
            "PENDING_PAYMENT",
            "PENDING_APPROVAL",
            "APPROVED",
            "REJECTED",
            "CANCELLED",
            name="request_status",
        ),
        nullable=False,
        default="PENDING_PAYMENT",
        index=True,
    )
    payment_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("payments.id"), nullable=True
    )
    reviewed_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rejection_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="meal_requests", foreign_keys=[user_id]
    )
    payment: Mapped[Optional["Payment"]] = relationship(
        "Payment", back_populates="request", foreign_keys=[payment_id]
    )
    reviewer: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[reviewed_by]
    )

    def __repr__(self) -> str:
        return f"<MealRequest {self.user_id} {self.date} {self.meal_type} {self.status}>"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    request_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(
        Enum("CASH", "MOBILE_BANKING", "BANK_TRANSFER", "OTHER", name="payment_method"),
        nullable=False,
    )
    reference_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("PENDING", "COMPLETED", "FAILED", "REFUNDED", name="payment_status"),
        nullable=False,
        default="PENDING",
        index=True,
    )
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="payments")
    request: Mapped[Optional["MealRequest"]] = relationship(
        "MealRequest", back_populates="payment", foreign_keys=[MealRequest.payment_id]
    )

    def __repr__(self) -> str:
        return f"<Payment {self.amount} {self.status}>"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    old_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    new_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), index=True
    )

    # Relationship
    user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} by {self.user_id}>"


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    key_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<SystemSetting {self.key_name}={self.value}>"
