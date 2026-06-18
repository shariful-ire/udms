from datetime import date, datetime, time, timezone
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictException,
    MealAlreadyExistsException,
    MealDeadlinePassedException,
    MealInactiveException,
    NotFoundException,
    PermissionDeniedException,
    ValidationException,
)
from app.models.expense import AuditLog, Expense, MealRequest, Payment
from app.models.meal import StudentMeal
from app.repositories.meal_repo import (
    AuditRepository,
    ExpenseRepository,
    MealRequestRepository,
    MealScheduleRepository,
    DailyMenuRepository,
    PaymentRepository,
    StudentMealRepository,
)
from app.repositories.user_repo import UserRepository
from app.schemas.meal import (
    ExpenseCreate,
    ExpenseUpdate,
    MealRequestCreate,
    PaymentSubmit,
    ReportData,
    MealBreakdown,
    ExpenseCategoryBreakdown,
    CustomerStats,
    TodayMealStatus,
)


# ─── Meal Service ─────────────────────────────────────────────────────────────
class MealService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.meal_repo = StudentMealRepository(db)
        self.schedule_repo = MealScheduleRepository(db)
        self.menu_repo = DailyMenuRepository(db)

    def _now_time(self) -> time:
        return datetime.now(timezone.utc).time()

    def _today(self) -> date:
        return datetime.now(timezone.utc).date()

    async def get_today_status(self, user_id: str) -> List[TodayMealStatus]:
        today = self._today()
        now = self._now_time()
        statuses = []

        for meal_type in ["BREAKFAST", "LUNCH", "DINNER"]:
            schedule = await self.schedule_repo.get_by_meal_type(meal_type)
            menu = await self.menu_repo.get_by_date_and_type(today, meal_type)
            meal = await self.meal_repo.get_user_meal(user_id, today, meal_type)

            can_add = False
            can_cancel = False
            is_active = False
            is_cancelled_by_manager = False

            if schedule and schedule.is_active:
                is_active = True
                if menu and menu.is_cancelled:
                    is_cancelled_by_manager = True
                else:
                    if meal is None or meal.status == "CANCELLED":
                        # Can add only before meal start time
                        can_add = now < schedule.start_time
                    if meal and meal.status == "ACTIVE":
                        # Can cancel only before cancel deadline
                        can_cancel = now < schedule.cancel_deadline

            statuses.append(
                TodayMealStatus(
                    meal_type=meal_type,
                    schedule=schedule,
                    menu=menu,
                    meal=meal,
                    can_add=can_add,
                    can_cancel=can_cancel,
                    is_active=is_active,
                    is_cancelled_by_manager=is_cancelled_by_manager,
                )
            )
        return statuses

    async def add_meal(self, user_id: str, meal_date: date, meal_type: str) -> StudentMeal:
        now = datetime.now(timezone.utc).time()

        schedule = await self.schedule_repo.get_by_meal_type(meal_type)
        if not schedule or not schedule.is_active:
            raise MealInactiveException(meal_type)

        # Check if cancelled by manager
        menu = await self.menu_repo.get_by_date_and_type(meal_date, meal_type)
        if menu and menu.is_cancelled:
            raise MealInactiveException(f"{meal_type} (cancelled by dining manager)")

        # Check deadline - must add before start time
        if meal_date == datetime.now(timezone.utc).date() and now >= schedule.start_time:
            raise MealDeadlinePassedException("add", meal_type)

        # Check duplicate
        existing = await self.meal_repo.get_user_meal(user_id, meal_date, meal_type)
        if existing and existing.status == "ACTIVE":
            raise MealAlreadyExistsException()

        if existing and existing.status == "CANCELLED":
            # Reactivate
            return await self.meal_repo.update(existing, {
                "status": "ACTIVE",
                "cancelled_at": None,
            })

        return await self.meal_repo.create({
            "user_id": user_id,
            "date": meal_date,
            "meal_type": meal_type,
            "status": "ACTIVE",
        })

    async def cancel_meal(self, user_id: str, meal_id: str) -> StudentMeal:
        meal = await self.meal_repo.get_by_id(meal_id)
        if not meal or meal.user_id != user_id:
            raise NotFoundException("Meal", meal_id)
        if meal.status != "ACTIVE":
            raise ValidationException("Meal is already cancelled")

        schedule = await self.schedule_repo.get_by_meal_type(meal.meal_type)
        if schedule:
            now = datetime.now(timezone.utc).time()
            if meal.date == datetime.now(timezone.utc).date() and now >= schedule.cancel_deadline:
                raise MealDeadlinePassedException("cancel", meal.meal_type)

        return await self.meal_repo.update(meal, {
            "status": "CANCELLED",
            "cancelled_at": datetime.now(timezone.utc),
        })

    async def get_history(
        self, user_id: str, *, page: int, per_page: int,
        month: Optional[int] = None, year: Optional[int] = None,
        meal_type: Optional[str] = None, status: Optional[str] = None,
    ) -> Tuple[List[StudentMeal], int]:
        return await self.meal_repo.get_user_history(
            user_id, page=page, per_page=per_page,
            month=month, year=year, meal_type=meal_type, status=status,
        )

    async def get_monthly_summary(self, user_id: str, year: int, month: int) -> dict:
        breakdown = await self.meal_repo.get_monthly_summary(user_id, year, month)
        total = sum(breakdown.values())
        return {
            "year": year,
            "month": month,
            "total": total,
            "breakdown": {
                "BREAKFAST": breakdown.get("BREAKFAST", 0),
                "LUNCH": breakdown.get("LUNCH", 0),
                "DINNER": breakdown.get("DINNER", 0),
            },
        }


# ─── Meal Request Service ─────────────────────────────────────────────────────
class MealRequestService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.request_repo = MealRequestRepository(db)
        self.payment_repo = PaymentRepository(db)
        self.meal_repo = StudentMealRepository(db)

    async def create_request(self, user_id: str, data: MealRequestCreate) -> MealRequest:
        return await self.request_repo.create({
            "user_id": user_id,
            "date": data.date,
            "meal_type": data.meal_type,
            "reason": data.reason,
            "status": "PENDING_PAYMENT",
        })

    async def submit_payment(self, user_id: str, data: PaymentSubmit) -> MealRequest:
        request = await self.request_repo.get_by_id(data.request_id)
        if not request or request.user_id != user_id:
            raise NotFoundException("MealRequest", data.request_id)
        if request.status != "PENDING_PAYMENT":
            raise ValidationException("This request is not awaiting payment")

        payment = await self.payment_repo.create({
            "user_id": user_id,
            "request_id": request.id,
            "amount": data.amount,
            "payment_method": data.payment_method,
            "reference_no": data.reference_no,
            "status": "COMPLETED",
            "note": data.note,
        })

        return await self.request_repo.update(request, {
            "payment_id": payment.id,
            "status": "PENDING_APPROVAL",
        })

    async def approve_request(self, request_id: str, reviewer_id: str) -> MealRequest:
        request = await self.request_repo.get_by_id(request_id)
        if not request:
            raise NotFoundException("MealRequest", request_id)
        if request.status != "PENDING_APPROVAL":
            raise ValidationException("Request is not pending approval")

        # Create student_meal record
        await self.meal_repo.create({
            "user_id": request.user_id,
            "date": request.date,
            "meal_type": request.meal_type,
            "status": "ACTIVE",
        })

        return await self.request_repo.update(request, {
            "status": "APPROVED",
            "reviewed_by": reviewer_id,
            "reviewed_at": datetime.now(timezone.utc),
        })

    async def reject_request(self, request_id: str, reviewer_id: str, note: str = None) -> MealRequest:
        request = await self.request_repo.get_by_id(request_id)
        if not request:
            raise NotFoundException("MealRequest", request_id)
        if request.status != "PENDING_APPROVAL":
            raise ValidationException("Request is not pending approval")

        return await self.request_repo.update(request, {
            "status": "REJECTED",
            "reviewed_by": reviewer_id,
            "reviewed_at": datetime.now(timezone.utc),
            "rejection_note": note,
        })

    async def cancel_request(self, user_id: str, request_id: str) -> MealRequest:
        request = await self.request_repo.get_by_id(request_id)
        if not request or request.user_id != user_id:
            raise NotFoundException("MealRequest", request_id)
        if request.status != "PENDING_PAYMENT":
            raise ValidationException("Only pending-payment requests can be cancelled")
        return await self.request_repo.update(request, {"status": "CANCELLED"})

    async def submit_payment_by_id(
        self, user_id: str, request_id: str,
        amount, payment_method: str, reference_no: Optional[str] = None, note: Optional[str] = None,
    ) -> MealRequest:
        request = await self.request_repo.get_by_id(request_id)
        if not request or request.user_id != user_id:
            raise NotFoundException("MealRequest", request_id)
        if request.status != "PENDING_PAYMENT":
            raise ValidationException("This request is not awaiting payment")
        payment = await self.payment_repo.create({
            "user_id": user_id,
            "request_id": request.id,
            "amount": amount,
            "payment_method": payment_method,
            "reference_no": reference_no,
            "status": "COMPLETED",
            "note": note,
        })
        await self.request_repo.update(request, {
            "payment_id": payment.id,
            "status": "PENDING_APPROVAL",
        })
        return await self.request_repo.get_by_id_with_relations(request_id)

    async def get_requests(
        self, *, page: int, per_page: int,
        user_id: Optional[str] = None, status: Optional[str] = None,
    ) -> Tuple[List[MealRequest], int]:
        return await self.request_repo.get_paginated(
            page=page, per_page=per_page, user_id=user_id, status=status
        )


# ─── Expense Service ──────────────────────────────────────────────────────────
class ExpenseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.expense_repo = ExpenseRepository(db)

    async def create(self, data: ExpenseCreate, user_id: str) -> Expense:
        return await self.expense_repo.create({
            "name": data.name,
            "category": data.category,
            "amount": data.amount,
            "description": data.description,
            "expense_date": data.expense_date,
            "created_by": user_id,
        })

    async def update(self, expense_id: str, data: ExpenseUpdate, user_id: str) -> Expense:
        expense = await self.expense_repo.get_by_id(expense_id)
        if not expense:
            raise NotFoundException("Expense", expense_id)
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        update_data["updated_by"] = user_id
        return await self.expense_repo.update(expense, update_data)

    async def delete(self, expense_id: str) -> bool:
        expense = await self.expense_repo.get_by_id(expense_id)
        if not expense:
            raise NotFoundException("Expense", expense_id)
        return await self.expense_repo.delete(expense)

    async def get_paginated(self, *, page: int, per_page: int, **filters) -> Tuple[List[Expense], int]:
        return await self.expense_repo.get_paginated(
            page=page, per_page=per_page, **filters
        )


# ─── Report Service ───────────────────────────────────────────────────────────
class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.meal_repo = StudentMealRepository(db)
        self.expense_repo = ExpenseRepository(db)
        self.payment_repo = PaymentRepository(db)
        self.user_repo = UserRepository(db)
        self.request_repo = MealRequestRepository(db)

    async def get_daily_breakdown(self, start: date, end: date) -> dict:
        from sqlalchemy import select, func, and_
        from app.models.meal import StudentMeal as SM
        r = await self.db.execute(
            select(SM.date, SM.meal_type, func.count(SM.id))
            .where(and_(SM.date >= start, SM.date <= end, SM.status == "ACTIVE"))
            .group_by(SM.date, SM.meal_type)
            .order_by(SM.date)
        )
        meal_by_day: dict = {}
        for row_date, meal_type, count in r.all():
            key = str(row_date)
            if key not in meal_by_day:
                meal_by_day[key] = {"date": key, "breakfast": 0, "lunch": 0, "dinner": 0}
            meal_by_day[key][meal_type.lower()] = count

        daily_income = {row["date"]: row["total"] for row in await self.payment_repo.get_daily_income(start, end)}
        daily_expense = {row["date"]: row["total"] for row in await self.expense_repo.get_daily_totals(start, end)}

        all_dates = sorted(set(list(meal_by_day) + list(daily_income) + list(daily_expense)))
        return {
            "breakdown": [
                {"period": d, "income": daily_income.get(d, 0), "expense": daily_expense.get(d, 0)}
                for d in all_dates
            ],
            "daily_breakdown": [
                meal_by_day.get(d, {"date": d, "breakfast": 0, "lunch": 0, "dinner": 0})
                for d in all_dates
            ],
        }

    async def generate(self, start: date, end: date) -> ReportData:
        # Meals
        breakdown_rows = {}
        for meal_type in ["BREAKFAST", "LUNCH", "DINNER"]:
            from sqlalchemy import select, func, and_
            from app.models.meal import StudentMeal
            r = await self.db.execute(
                select(func.count()).select_from(StudentMeal).where(
                    and_(
                        StudentMeal.date >= start,
                        StudentMeal.date <= end,
                        StudentMeal.status == "ACTIVE",
                        StudentMeal.meal_type == meal_type,
                    )
                )
            )
            breakdown_rows[meal_type] = r.scalar() or 0

        total_meals = sum(breakdown_rows.values())

        # Count non-customer (approved request) meals
        from app.models.expense import MealRequest
        from sqlalchemy import select, func, and_
        r = await self.db.execute(
            select(func.count()).select_from(MealRequest).where(
                and_(
                    MealRequest.date >= start,
                    MealRequest.date <= end,
                    MealRequest.status == "APPROVED",
                )
            )
        )
        non_customer_meals = r.scalar() or 0
        customer_meals = total_meals - non_customer_meals

        # Income
        income_total = await self.payment_repo.sum_income_in_range(start, end)

        # Expenses
        expenses_total = await self.expense_repo.sum_in_range(start, end)
        expense_by_cat = await self.expense_repo.sum_by_category_in_range(start, end)

        # Customers
        r = await self.db.execute(
            select(func.count()).select_from(
                __import__("app.models.user", fromlist=["User"]).User
            ).where(
                __import__("app.models.user", fromlist=["User"]).User.role == "CUSTOMER"
            )
        )
        total_customers = r.scalar() or 0

        return ReportData(
            period_start=start,
            period_end=end,
            meals=MealBreakdown(
                breakfast=breakdown_rows.get("BREAKFAST", 0),
                lunch=breakdown_rows.get("LUNCH", 0),
                dinner=breakdown_rows.get("DINNER", 0),
            ),
            total_meals_served=total_meals,
            customer_meals=customer_meals,
            non_customer_meals=non_customer_meals,
            income_total=income_total,
            income_from_requests=income_total,
            expenses_total=expenses_total,
            expenses_by_category=ExpenseCategoryBreakdown(
                **{k: v for k, v in expense_by_cat.items()}
            ),
            net=income_total - expenses_total,
            customers=CustomerStats(
                total_enrolled=total_customers,
                active_this_period=customer_meals,
            ),
            per_meal_cost=(
                Decimal(str(expenses_total)) / Decimal(str(total_meals))
                if total_meals > 0
                else None
            ),
        )
