from datetime import date, datetime, time, timedelta, timezone
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
from app.models.expense import AuditLog, Earning, Expense, MealRequest, MemberPayment, Payment, PaymentProof
from app.models.meal import StudentMeal
from app.repositories.meal_repo import (
    AuditRepository,
    EarningRepository,
    ExpenseRepository,
    MealRequestRepository,
    MealScheduleRepository,
    MemberPaymentRepository,
    DailyMenuRepository,
    PaymentProofRepository,
    PaymentRepository,
    StudentMealRepository,
)
from app.repositories.user_repo import UserRepository
from app.schemas.meal import (
    DashboardStats,
    EarningCreate,
    EarningUpdate,
    ExpenseCreate,
    ExpenseUpdate,
    MealRequestCreate,
    MealSessionStats,
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


# ─── Earning Service ─────────────────────────────────────────────────────────
class EarningService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.earning_repo = EarningRepository(db)

    async def create(self, data: EarningCreate, user_id: str) -> Earning:
        return await self.earning_repo.create({
            "description": data.description,
            "category": data.category,
            "amount": data.amount,
            "earning_date": data.earning_date,
            "notes": data.notes,
            "created_by": user_id,
        })

    async def update(self, earning_id: str, data: EarningUpdate, user_id: str) -> Earning:
        earning = await self.earning_repo.get_by_id(earning_id)
        if not earning:
            raise NotFoundException("Earning", earning_id)
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        return await self.earning_repo.update(earning, update_data)

    async def delete(self, earning_id: str) -> bool:
        earning = await self.earning_repo.get_by_id(earning_id)
        if not earning:
            raise NotFoundException("Earning", earning_id)
        return await self.earning_repo.delete(earning)

    async def get_paginated(self, *, page: int, per_page: int, **filters) -> Tuple[List[Earning], int]:
        return await self.earning_repo.get_paginated(page=page, per_page=per_page, **filters)


# ─── Dashboard Service ───────────────────────────────────────────────────────
class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.expense_repo = ExpenseRepository(db)
        self.earning_repo = EarningRepository(db)
        self.meal_repo = StudentMealRepository(db)
        self.user_repo = UserRepository(db)

    async def get_stats(self) -> DashboardStats:
        from sqlalchemy import select, func, and_

        total_expenses = await self.expense_repo.sum_all()
        total_earnings = await self.earning_repo.sum_all()

        # Active customers count
        from app.models.user import User
        r = await self.db.execute(
            select(func.count()).select_from(User).where(
                and_(User.role == "CUSTOMER", User.status == "ACTIVE")
            )
        )
        active_customers = r.scalar() or 0

        # Current 7-day session (Mon-Sun of current week)
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Total possible meals = active_customers × 3 meals/day × 7 days
        total_possible = active_customers * 3 * 7

        # Consumed meals this session
        from app.models.meal import StudentMeal
        r = await self.db.execute(
            select(func.count()).select_from(StudentMeal).where(
                and_(
                    StudentMeal.date >= start_of_week,
                    StudentMeal.date <= end_of_week,
                    StudentMeal.status == "ACTIVE",
                )
            )
        )
        consumed = r.scalar() or 0
        remaining = max(0, total_possible - consumed)

        # Expenses for the current session
        session_expenses = await self.expense_repo.sum_in_range(start_of_week, end_of_week)

        per_meal_cost = None
        remaining_cost = None
        if consumed > 0:
            per_meal_cost = Decimal(str(session_expenses)) / Decimal(str(consumed))
            remaining_cost = per_meal_cost * Decimal(str(remaining))
        elif total_possible > 0:
            per_meal_cost = Decimal(str(session_expenses)) / Decimal(str(total_possible))
            remaining_cost = per_meal_cost * Decimal(str(remaining))

        return DashboardStats(
            total_expenses=total_expenses,
            total_earnings=total_earnings,
            net_balance=total_earnings - total_expenses,
            active_customers=active_customers,
            session=MealSessionStats(
                start_date=start_of_week,
                end_date=end_of_week,
                total_possible_meals=total_possible,
                consumed_meals=consumed,
                remaining_meals=remaining,
                per_meal_cost=per_meal_cost,
                remaining_cost=remaining_cost,
            ),
        )


# ─── Member Payment Service ──────────────────────────────────────────────────
class MemberPaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repo = MemberPaymentRepository(db)
        self.proof_repo = PaymentProofRepository(db)

    async def get_or_create(self, user_id: str, year: int, month: int, amount_due: Decimal = Decimal("0.00")) -> MemberPayment:
        existing = await self.payment_repo.get_by_user_month(user_id, year, month)
        if existing:
            return existing
        return await self.payment_repo.create({
            "user_id": user_id,
            "year": year,
            "month": month,
            "amount_due": amount_due,
            "amount_paid": Decimal("0.00"),
            "status": "PENDING",
        })

    async def mark_paid(self, payment_id: str) -> MemberPayment:
        payment = await self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise NotFoundException("MemberPayment", payment_id)
        return await self.payment_repo.update(payment, {"status": "PAID"})

    async def mark_pending(self, payment_id: str) -> MemberPayment:
        payment = await self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise NotFoundException("MemberPayment", payment_id)
        return await self.payment_repo.update(payment, {"status": "PENDING"})

    async def get_paginated(self, **kwargs) -> Tuple[List[MemberPayment], int]:
        return await self.payment_repo.get_paginated(**kwargs)

    async def get_summary(self, year: int, month: int) -> dict:
        counts = await self.payment_repo.count_by_status(year, month)
        proof_counts = {}
        from sqlalchemy import select, func as sqlfunc, and_ as sqland
        for ps in ["SUBMITTED", "APPROVED", "REJECTED"]:
            r = await self.db.execute(
                select(sqlfunc.count()).select_from(PaymentProof).where(PaymentProof.status == ps)
            )
            proof_counts[ps.lower()] = r.scalar() or 0
        return {
            "paid": counts.get("PAID", 0),
            "pending": counts.get("PENDING", 0),
            "proofs_submitted": proof_counts.get("submitted", 0),
            "proofs_approved": proof_counts.get("approved", 0),
            "proofs_rejected": proof_counts.get("rejected", 0),
        }

    async def submit_proof(self, user_id: str, member_payment_id: str, proof_type: str, proof_value: str) -> PaymentProof:
        payment = await self.payment_repo.get_by_id(member_payment_id)
        if not payment:
            raise NotFoundException("MemberPayment", member_payment_id)
        if payment.user_id != user_id:
            raise PermissionDeniedException("You can only submit proofs for your own payments")
        return await self.proof_repo.create({
            "member_payment_id": member_payment_id,
            "user_id": user_id,
            "proof_type": proof_type,
            "proof_value": proof_value,
            "status": "SUBMITTED",
        })

    async def approve_proof(self, proof_id: str, reviewer_id: str) -> PaymentProof:
        proof = await self.proof_repo.get_by_id(proof_id)
        if not proof:
            raise NotFoundException("PaymentProof", proof_id)
        updated = await self.proof_repo.update(proof, {
            "status": "APPROVED",
            "reviewed_by": reviewer_id,
            "reviewed_at": datetime.now(timezone.utc),
        })
        payment = await self.payment_repo.get_by_id(proof.member_payment_id)
        if payment:
            await self.payment_repo.update(payment, {"status": "PAID"})
        return updated

    async def reject_proof(self, proof_id: str, reviewer_id: str, note: str = None) -> PaymentProof:
        proof = await self.proof_repo.get_by_id(proof_id)
        if not proof:
            raise NotFoundException("PaymentProof", proof_id)
        return await self.proof_repo.update(proof, {
            "status": "REJECTED",
            "reviewed_by": reviewer_id,
            "reviewed_at": datetime.now(timezone.utc),
            "rejection_note": note,
        })

    async def get_proofs(self, **kwargs) -> Tuple[List[PaymentProof], int]:
        return await self.proof_repo.get_paginated(**kwargs)

    async def init_month_for_active_customers(self, year: int, month: int, amount_due: Decimal = Decimal("0.00")) -> int:
        from app.models.user import User
        from sqlalchemy import select, and_
        r = await self.db.execute(
            select(User.id).where(and_(User.role == "CUSTOMER", User.status == "ACTIVE"))
        )
        user_ids = [row[0] for row in r.all()]
        created = 0
        for uid in user_ids:
            existing = await self.payment_repo.get_by_user_month(uid, year, month)
            if not existing:
                await self.payment_repo.create({
                    "user_id": uid, "year": year, "month": month,
                    "amount_due": amount_due, "amount_paid": Decimal("0.00"), "status": "PENDING",
                })
                created += 1
        return created
