from datetime import date, datetime, time
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


# ─── Meal Schedule Schemas ───────────────────────────────────────────────────
class MealScheduleResponse(BaseModel):
    id: str
    meal_type: str
    start_time: time
    end_time: time
    cancel_deadline: time
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MealScheduleUpdate(BaseModel):
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    cancel_deadline: Optional[time] = None
    is_active: Optional[bool] = None


# ─── Daily Menu Schemas ───────────────────────────────────────────────────────
class MenuItemCreate(BaseModel):
    food_name: str = Field(..., min_length=1, max_length=200)
    quantity: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class MenuItemResponse(BaseModel):
    id: str
    food_name: str
    quantity: Optional[str] = None
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class DailyMenuCreate(BaseModel):
    date: date
    meal_type: str = Field(..., pattern=r"^(BREAKFAST|LUNCH|DINNER)$")
    items: List[MenuItemCreate] = Field(..., min_length=1)


class DailyMenuUpdate(BaseModel):
    items: Optional[List[MenuItemCreate]] = None
    is_cancelled: Optional[bool] = None


class DailyMenuResponse(BaseModel):
    id: str
    date: date
    meal_type: str
    is_cancelled: bool
    items: List[MenuItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Student Meal Schemas ─────────────────────────────────────────────────────
class StudentMealCreate(BaseModel):
    date: date
    meal_type: str = Field(..., pattern=r"^(BREAKFAST|LUNCH|DINNER)$")


class StudentMealResponse(BaseModel):
    id: str
    user_id: str
    date: date
    meal_type: str
    status: str
    cancelled_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TodayMealStatus(BaseModel):
    meal_type: str
    schedule: Optional[MealScheduleResponse] = None
    menu: Optional[DailyMenuResponse] = None
    meal: Optional[StudentMealResponse] = None
    can_add: bool
    can_cancel: bool
    is_active: bool
    is_cancelled_by_manager: bool


# ─── Expense Schemas ──────────────────────────────────────────────────────────
class ExpenseCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    category: str = Field(
        ...,
        pattern=r"^(FOOD_PURCHASE|UTILITIES|SALARY|EQUIPMENT|MAINTENANCE|MISCELLANEOUS)$",
    )
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    description: Optional[str] = None
    expense_date: date


class ExpenseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    category: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    description: Optional[str] = None
    expense_date: Optional[date] = None


class ExpenseResponse(BaseModel):
    id: str
    name: str
    category: str
    amount: Decimal
    description: Optional[str] = None
    expense_date: date
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Earning Schemas ─────────────────────────────────────────────────────────
class EarningCreate(BaseModel):
    description: str = Field(..., min_length=2, max_length=200)
    category: str = Field(
        ...,
        pattern=r"^(MEAL_PAYMENT|DEPOSIT|GRANT|OTHER)$",
    )
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    earning_date: date
    notes: Optional[str] = None


class EarningUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=2, max_length=200)
    category: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    earning_date: Optional[date] = None
    notes: Optional[str] = None


class EarningResponse(BaseModel):
    id: str
    description: str
    category: str
    amount: Decimal
    earning_date: date
    notes: Optional[str] = None
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Dashboard Stats Schema ─────────────────────────────────────────────────
class MealSessionStats(BaseModel):
    start_date: date
    end_date: date
    total_possible_meals: int
    consumed_meals: int
    remaining_meals: int
    per_meal_cost: Optional[Decimal] = None
    remaining_cost: Optional[Decimal] = None


class DashboardStats(BaseModel):
    total_expenses: Decimal
    total_earnings: Decimal
    net_balance: Decimal
    active_customers: int
    session: MealSessionStats


# ─── Meal Request Schemas ─────────────────────────────────────────────────────
class MealRequestCreate(BaseModel):
    date: date
    meal_type: str = Field(..., pattern=r"^(BREAKFAST|LUNCH|DINNER)$")
    reason: Optional[str] = None


class MealRequestReview(BaseModel):
    rejection_note: Optional[str] = None


class PaymentCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    payment_method: str = Field(
        ...,
        pattern=r"^(CASH|MOBILE_BANKING|BANK_TRANSFER|OTHER)$",
    )
    transaction_id: Optional[str] = Field(None, max_length=100)
    payment_date: Optional[date] = None
    note: Optional[str] = None


class PaymentSubmit(BaseModel):
    request_id: str
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    payment_method: str = Field(
        ...,
        pattern=r"^(CASH|MOBILE_BANKING|BANK_TRANSFER|OTHER)$",
    )
    reference_no: Optional[str] = Field(None, max_length=100)
    note: Optional[str] = None


class MealRequestResponse(BaseModel):
    id: str
    user_id: str
    date: date
    meal_type: str
    reason: Optional[str] = None
    status: str
    payment_id: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    rejection_note: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MealRequestDetailResponse(MealRequestResponse):
    student_name: Optional[str] = None
    student_username: Optional[str] = None
    student_email: Optional[str] = None
    payment_amount: Optional[Decimal] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None


# ─── Payment Schemas ──────────────────────────────────────────────────────────
class PaymentResponse(BaseModel):
    id: str
    user_id: str
    request_id: Optional[str] = None
    amount: Decimal
    payment_method: str
    reference_no: Optional[str] = None
    status: str
    note: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Report Schemas ───────────────────────────────────────────────────────────
class MealBreakdown(BaseModel):
    breakfast: int = 0
    lunch: int = 0
    dinner: int = 0


class ExpenseCategoryBreakdown(BaseModel):
    FOOD_PURCHASE: Decimal = Decimal("0.00")
    UTILITIES: Decimal = Decimal("0.00")
    SALARY: Decimal = Decimal("0.00")
    EQUIPMENT: Decimal = Decimal("0.00")
    MAINTENANCE: Decimal = Decimal("0.00")
    MISCELLANEOUS: Decimal = Decimal("0.00")


class CustomerStats(BaseModel):
    total_enrolled: int = 0
    active_this_period: int = 0


class ReportData(BaseModel):
    period_start: date
    period_end: date
    meals: MealBreakdown
    total_meals_served: int
    customer_meals: int
    non_customer_meals: int
    income_total: Decimal
    income_from_requests: Decimal
    expenses_total: Decimal
    expenses_by_category: ExpenseCategoryBreakdown
    net: Decimal
    customers: CustomerStats
    per_meal_cost: Optional[Decimal] = None
