import uuid
from datetime import date, datetime, time
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MealSchedule(Base):
    __tablename__ = "meal_schedules"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    meal_type: Mapped[str] = mapped_column(
        Enum("BREAKFAST", "LUNCH", "DINNER", name="meal_type_enum"),
        nullable=False,
        unique=True,
    )
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    cancel_deadline: Mapped[time] = mapped_column(Time, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    updated_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<MealSchedule {self.meal_type} {self.start_time}-{self.end_time}>"


class DailyMenu(Base):
    __tablename__ = "daily_menus"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    meal_type: Mapped[str] = mapped_column(
        Enum("BREAKFAST", "LUNCH", "DINNER", name="meal_type_menu"),
        nullable=False,
    )
    is_cancelled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    updated_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    items: Mapped[List["MenuItem"]] = relationship(
        "MenuItem", back_populates="menu", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("date", "meal_type", name="uq_date_meal_type"),
    )

    def __repr__(self) -> str:
        return f"<DailyMenu {self.date} {self.meal_type}>"


class MenuItem(Base):
    __tablename__ = "menu_items"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    menu_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("daily_menus.id", ondelete="CASCADE"), nullable=False, index=True
    )
    food_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())

    # Relationship
    menu: Mapped["DailyMenu"] = relationship("DailyMenu", back_populates="items")

    def __repr__(self) -> str:
        return f"<MenuItem {self.food_name}>"


class StudentMeal(Base):
    __tablename__ = "student_meals"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    meal_type: Mapped[str] = mapped_column(
        Enum("BREAKFAST", "LUNCH", "DINNER", name="meal_type_student"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Enum("ACTIVE", "CANCELLED", name="student_meal_status"),
        nullable=False,
        default="ACTIVE",
        index=True,
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="student_meals")

    __table_args__ = (
        UniqueConstraint("user_id", "date", "meal_type", name="uq_user_date_meal"),
    )

    def __repr__(self) -> str:
        return f"<StudentMeal user={self.user_id} {self.date} {self.meal_type}>"
