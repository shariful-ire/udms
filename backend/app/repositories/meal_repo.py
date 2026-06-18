from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.meal import DailyMenu, MealSchedule, MenuItem, StudentMeal
from app.models.expense import AuditLog, Earning, Expense, MealRequest, Payment
from app.repositories.base import BaseRepository


# ─── Meal Schedule Repository ─────────────────────────────────────────────────
class MealScheduleRepository(BaseRepository[MealSchedule]):
    def __init__(self, db: AsyncSession):
        super().__init__(MealSchedule, db)

    async def get_by_meal_type(self, meal_type: str) -> Optional[MealSchedule]:
        r = await self.db.execute(
            select(MealSchedule).where(MealSchedule.meal_type == meal_type)
        )
        return r.scalars().first()

    async def get_all_active(self) -> List[MealSchedule]:
        r = await self.db.execute(
            select(MealSchedule).where(MealSchedule.is_active == True)
        )
        return list(r.scalars().all())

    async def get_all_schedules(self) -> List[MealSchedule]:
        r = await self.db.execute(
            select(MealSchedule).order_by(MealSchedule.start_time)
        )
        return list(r.scalars().all())


# ─── Daily Menu Repository ────────────────────────────────────────────────────
class DailyMenuRepository(BaseRepository[DailyMenu]):
    def __init__(self, db: AsyncSession):
        super().__init__(DailyMenu, db)

    async def get_by_date_and_type(self, menu_date: date, meal_type: str) -> Optional[DailyMenu]:
        r = await self.db.execute(
            select(DailyMenu)
            .options(selectinload(DailyMenu.items))
            .where(and_(DailyMenu.date == menu_date, DailyMenu.meal_type == meal_type))
        )
        return r.scalars().first()

    async def get_by_date(self, menu_date: date) -> List[DailyMenu]:
        r = await self.db.execute(
            select(DailyMenu)
            .options(selectinload(DailyMenu.items))
            .where(DailyMenu.date == menu_date)
            .order_by(DailyMenu.meal_type)
        )
        return list(r.scalars().all())

    async def get_range(self, start: date, end: date) -> List[DailyMenu]:
        r = await self.db.execute(
            select(DailyMenu)
            .options(selectinload(DailyMenu.items))
            .where(and_(DailyMenu.date >= start, DailyMenu.date <= end))
            .order_by(DailyMenu.date, DailyMenu.meal_type)
        )
        return list(r.scalars().all())


# ─── Student Meal Repository ──────────────────────────────────────────────────
class StudentMealRepository(BaseRepository[StudentMeal]):
    def __init__(self, db: AsyncSession):
        super().__init__(StudentMeal, db)

    async def get_user_meal(self, user_id: str, meal_date: date, meal_type: str) -> Optional[StudentMeal]:
        r = await self.db.execute(
            select(StudentMeal).where(
                and_(
                    StudentMeal.user_id == user_id,
                    StudentMeal.date == meal_date,
                    StudentMeal.meal_type == meal_type,
                )
            )
        )
        return r.scalars().first()

    async def get_user_today_meals(self, user_id: str, meal_date: date) -> List[StudentMeal]:
        r = await self.db.execute(
            select(StudentMeal).where(
                and_(StudentMeal.user_id == user_id, StudentMeal.date == meal_date)
            )
        )
        return list(r.scalars().all())

    async def get_user_history(
        self, user_id: str, *, page: int = 1, per_page: int = 20,
        month: Optional[int] = None, year: Optional[int] = None,
        meal_type: Optional[str] = None, status: Optional[str] = None,
    ) -> Tuple[List[StudentMeal], int]:
        conditions = [StudentMeal.user_id == user_id]
        if month and year:
            from sqlalchemy import extract
            conditions.append(extract("month", StudentMeal.date) == month)
            conditions.append(extract("year", StudentMeal.date) == year)
        if meal_type:
            conditions.append(StudentMeal.meal_type == meal_type)
        if status:
            conditions.append(StudentMeal.status == status)

        q = select(StudentMeal).where(and_(*conditions))
        cq = select(func.count()).select_from(StudentMeal).where(and_(*conditions))
        total = (await self.db.execute(cq)).scalar() or 0
        offset = (page - 1) * per_page
        items = (
            await self.db.execute(q.order_by(StudentMeal.date.desc()).offset(offset).limit(per_page))
        ).scalars().all()
        return list(items), total

    async def get_monthly_summary(self, user_id: str, year: int, month: int) -> dict:
        from sqlalchemy import extract
        r = await self.db.execute(
            select(StudentMeal.meal_type, func.count(StudentMeal.id))
            .where(
                and_(
                    StudentMeal.user_id == user_id,
                    StudentMeal.status == "ACTIVE",
                    extract("year", StudentMeal.date) == year,
                    extract("month", StudentMeal.date) == month,
                )
            )
            .group_by(StudentMeal.meal_type)
        )
        return {row[0]: row[1] for row in r.all()}

    async def count_served_on_date(self, meal_date: date, meal_type: Optional[str] = None) -> int:
        conditions = [StudentMeal.date == meal_date, StudentMeal.status == "ACTIVE"]
        if meal_type:
            conditions.append(StudentMeal.meal_type == meal_type)
        r = await self.db.execute(
            select(func.count()).select_from(StudentMeal).where(and_(*conditions))
        )
        return r.scalar() or 0


# ─── Meal Request Repository ──────────────────────────────────────────────────
class MealRequestRepository(BaseRepository[MealRequest]):
    def __init__(self, db: AsyncSession):
        super().__init__(MealRequest, db)

    async def get_paginated(
        self, *, page: int = 1, per_page: int = 20,
        user_id: Optional[str] = None, status: Optional[str] = None,
    ) -> Tuple[List[MealRequest], int]:
        conditions = []
        if user_id:
            conditions.append(MealRequest.user_id == user_id)
        if status:
            conditions.append(MealRequest.status == status)

        q = select(MealRequest).options(
            selectinload(MealRequest.user),
            selectinload(MealRequest.payment),
        )
        cq = select(func.count()).select_from(MealRequest)
        if conditions:
            q = q.where(and_(*conditions))
            cq = cq.where(and_(*conditions))

        total = (await self.db.execute(cq)).scalar() or 0
        offset = (page - 1) * per_page
        items = (
            await self.db.execute(q.order_by(MealRequest.created_at.desc()).offset(offset).limit(per_page))
        ).scalars().all()
        return list(items), total

    async def get_by_id_with_relations(self, request_id: str) -> Optional[MealRequest]:
        r = await self.db.execute(
            select(MealRequest)
            .options(
                selectinload(MealRequest.user),
                selectinload(MealRequest.payment),
            )
            .where(MealRequest.id == request_id)
        )
        return r.scalars().first()

    async def count_pending(self) -> int:
        r = await self.db.execute(
            select(func.count()).select_from(MealRequest).where(
                MealRequest.status == "PENDING_APPROVAL"
            )
        )
        return r.scalar() or 0


# ─── Payment Repository ───────────────────────────────────────────────────────
class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, db: AsyncSession):
        super().__init__(Payment, db)

    async def get_user_payments(
        self, user_id: str, *, page: int = 1, per_page: int = 20
    ) -> Tuple[List[Payment], int]:
        q = select(Payment).where(Payment.user_id == user_id)
        cq = select(func.count()).select_from(Payment).where(Payment.user_id == user_id)
        total = (await self.db.execute(cq)).scalar() or 0
        offset = (page - 1) * per_page
        items = (
            await self.db.execute(q.order_by(Payment.created_at.desc()).offset(offset).limit(per_page))
        ).scalars().all()
        return list(items), total

    async def get_daily_income(self, start: date, end: date) -> List[dict]:
        r = await self.db.execute(
            select(func.date(Payment.created_at).label("day"), func.sum(Payment.amount).label("total"))
            .where(
                and_(
                    Payment.status == "COMPLETED",
                    func.date(Payment.created_at) >= start,
                    func.date(Payment.created_at) <= end,
                )
            )
            .group_by(func.date(Payment.created_at))
            .order_by(func.date(Payment.created_at))
        )
        return [{"date": str(row[0]), "total": float(row[1] or 0)} for row in r.all()]

    async def sum_income_in_range(self, start: date, end: date) -> Decimal:
        from sqlalchemy import cast, Date as SADate
        r = await self.db.execute(
            select(func.sum(Payment.amount)).where(
                and_(
                    Payment.status == "COMPLETED",
                    func.date(Payment.created_at) >= start,
                    func.date(Payment.created_at) <= end,
                )
            )
        )
        return r.scalar() or Decimal("0.00")


# ─── Expense Repository ───────────────────────────────────────────────────────
class ExpenseRepository(BaseRepository[Expense]):
    def __init__(self, db: AsyncSession):
        super().__init__(Expense, db)

    async def get_paginated(
        self, *, page: int = 1, per_page: int = 20,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Tuple[List[Expense], int]:
        conditions = []
        if category:
            conditions.append(Expense.category == category)
        if start_date:
            conditions.append(Expense.expense_date >= start_date)
        if end_date:
            conditions.append(Expense.expense_date <= end_date)

        q = select(Expense)
        cq = select(func.count()).select_from(Expense)
        if conditions:
            q = q.where(and_(*conditions))
            cq = cq.where(and_(*conditions))

        total = (await self.db.execute(cq)).scalar() or 0
        offset = (page - 1) * per_page
        items = (
            await self.db.execute(q.order_by(Expense.expense_date.desc()).offset(offset).limit(per_page))
        ).scalars().all()
        return list(items), total

    async def sum_all(self) -> Decimal:
        r = await self.db.execute(select(func.sum(Expense.amount)))
        return r.scalar() or Decimal("0.00")

    async def sum_in_range(self, start: date, end: date) -> Decimal:
        r = await self.db.execute(
            select(func.sum(Expense.amount)).where(
                and_(Expense.expense_date >= start, Expense.expense_date <= end)
            )
        )
        return r.scalar() or Decimal("0.00")

    async def sum_by_category_in_range(self, start: date, end: date) -> dict:
        r = await self.db.execute(
            select(Expense.category, func.sum(Expense.amount)).where(
                and_(Expense.expense_date >= start, Expense.expense_date <= end)
            ).group_by(Expense.category)
        )
        return {row[0]: row[1] or Decimal("0.00") for row in r.all()}

    async def get_daily_totals(self, start: date, end: date) -> List[dict]:
        r = await self.db.execute(
            select(Expense.expense_date, func.sum(Expense.amount).label("total"))
            .where(and_(Expense.expense_date >= start, Expense.expense_date <= end))
            .group_by(Expense.expense_date)
            .order_by(Expense.expense_date)
        )
        return [{"date": str(row[0]), "total": float(row[1] or 0)} for row in r.all()]


# ─── Earning Repository ──────────────────────────────────────────────────────
class EarningRepository(BaseRepository[Earning]):
    def __init__(self, db: AsyncSession):
        super().__init__(Earning, db)

    async def get_paginated(
        self, *, page: int = 1, per_page: int = 20,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Tuple[List[Earning], int]:
        conditions = []
        if category:
            conditions.append(Earning.category == category)
        if start_date:
            conditions.append(Earning.earning_date >= start_date)
        if end_date:
            conditions.append(Earning.earning_date <= end_date)

        q = select(Earning)
        cq = select(func.count()).select_from(Earning)
        if conditions:
            q = q.where(and_(*conditions))
            cq = cq.where(and_(*conditions))

        total = (await self.db.execute(cq)).scalar() or 0
        offset = (page - 1) * per_page
        items = (
            await self.db.execute(q.order_by(Earning.earning_date.desc()).offset(offset).limit(per_page))
        ).scalars().all()
        return list(items), total

    async def sum_in_range(self, start: date, end: date) -> Decimal:
        r = await self.db.execute(
            select(func.sum(Earning.amount)).where(
                and_(Earning.earning_date >= start, Earning.earning_date <= end)
            )
        )
        return r.scalar() or Decimal("0.00")

    async def sum_all(self) -> Decimal:
        r = await self.db.execute(select(func.sum(Earning.amount)))
        return r.scalar() or Decimal("0.00")


# ─── Audit Repository ─────────────────────────────────────────────────────────
class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(AuditLog, db)

    async def get_paginated(
        self, *, page: int = 1, per_page: int = 20,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Tuple[List[AuditLog], int]:
        conditions = []
        if user_id:
            conditions.append(AuditLog.user_id == user_id)
        if action:
            conditions.append(AuditLog.action == action)
        if entity_type:
            conditions.append(AuditLog.entity_type == entity_type)
        if start_date:
            conditions.append(func.date(AuditLog.created_at) >= start_date)
        if end_date:
            conditions.append(func.date(AuditLog.created_at) <= end_date)

        q = select(AuditLog)
        cq = select(func.count()).select_from(AuditLog)
        if conditions:
            q = q.where(and_(*conditions))
            cq = cq.where(and_(*conditions))

        total = (await self.db.execute(cq)).scalar() or 0
        offset = (page - 1) * per_page
        items = (
            await self.db.execute(q.order_by(AuditLog.created_at.desc()).offset(offset).limit(per_page))
        ).scalars().all()
        return list(items), total

    async def get_recent(self, limit: int = 10) -> List[AuditLog]:
        r = await self.db.execute(
            select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        )
        return list(r.scalars().all())

    async def log(
        self,
        *,
        user_id: Optional[str],
        action: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        old_value: Optional[dict] = None,
        new_value: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        return await self.create({
            "user_id": user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "old_value": old_value,
            "new_value": new_value,
            "ip_address": ip_address,
            "user_agent": user_agent,
        })
