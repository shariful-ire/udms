from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_active_user, get_db
from app.core.permissions import UserRole, require_roles, require_permission, Permission
from app.models.user import User
from app.schemas.meal import (
    DailyMenuCreate,
    DailyMenuUpdate,
    EarningCreate,
    EarningUpdate,
    MealScheduleUpdate,
    StudentMealCreate,
    MealRequestCreate,
    MealRequestReview,
    PaymentSubmit,
    PaymentCreate,
    ExpenseCreate,
    ExpenseUpdate,
)
from app.services.dining_service import DiningService
from app.services.meal_service import MealService, MealRequestService, ExpenseService, EarningService, MemberPaymentService, DashboardService, ReportService


# ─── Serialization helpers ────────────────────────────────────────────────────

def _user_dict(user) -> Optional[dict]:
    if not user:
        return None
    return {
        "id": user.id,
        "full_name": user.full_name,
        "username": user.username,
        "email": user.email,
        "student_id": user.student_id,
        "department": user.department,
        "hall_name": user.hall_name,
        "batch": user.batch,
        "avatar_url": user.profile_image,
        "role": user.role,
    }


def _payment_dict(payment) -> Optional[dict]:
    if not payment:
        return None
    return {
        "id": payment.id,
        "amount": float(payment.amount),
        "payment_method": payment.payment_method,
        "reference_no": payment.reference_no,
        "status": payment.status,
        "note": payment.note,
        "created_at": payment.created_at.isoformat(),
    }


def _request_dict(request) -> dict:
    try:
        user = request.user
    except Exception:
        user = None
    try:
        payment = request.payment
    except Exception:
        payment = None
    return {
        "id": request.id,
        "user_id": request.user_id,
        "date": str(request.date),
        "meal_type": request.meal_type,
        "reason": request.reason,
        "status": request.status,
        "payment_id": request.payment_id,
        "reviewed_by": request.reviewed_by,
        "reviewed_at": request.reviewed_at.isoformat() if request.reviewed_at else None,
        "rejection_reason": request.rejection_note,
        "created_at": request.created_at.isoformat(),
        "updated_at": request.updated_at.isoformat(),
        "user": _user_dict(user),
        "payment": _payment_dict(payment),
    }


def _expense_dict(expense) -> dict:
    return {
        "id": expense.id,
        "name": expense.name,
        "category": expense.category,
        "amount": float(expense.amount),
        "description": expense.description,
        "date": str(expense.expense_date),
        "expense_date": str(expense.expense_date),
        "created_by": expense.created_by,
        "created_at": expense.created_at.isoformat(),
        "updated_at": expense.updated_at.isoformat(),
    }


def _earning_dict(earning) -> dict:
    return {
        "id": earning.id,
        "description": earning.description,
        "category": earning.category,
        "amount": float(earning.amount),
        "earning_date": str(earning.earning_date),
        "date": str(earning.earning_date),
        "notes": earning.notes,
        "created_by": earning.created_by,
        "created_at": earning.created_at.isoformat(),
        "updated_at": earning.updated_at.isoformat(),
    }


def _audit_dict(log) -> dict:
    try:
        actor = log.user
    except Exception:
        actor = None
    return {
        "id": log.id,
        "action": log.action,
        "entity_type": log.entity_type,
        "entity_id": log.entity_id,
        "ip_address": log.ip_address,
        "created_at": log.created_at.isoformat(),
        "target_description": f"{log.entity_type} {log.entity_id}" if log.entity_id else log.entity_type,
        "actor_name": actor.full_name if actor else "System",
        "actor": {
            "id": actor.id,
            "full_name": actor.full_name,
            "avatar_url": actor.profile_image,
        } if actor else None,
    }


def _format_report(report, daily_data: dict) -> dict:
    ec = report.expenses_by_category.model_dump()
    expense_by_category = [
        {"category": k, "amount": float(v)}
        for k, v in ec.items()
        if float(v) > 0
    ]
    return {
        "period_start": str(report.period_start),
        "period_end": str(report.period_end),
        "total_income": float(report.income_total),
        "total_expense": float(report.expenses_total),
        "total_meals": report.total_meals_served,
        "net": float(report.net),
        "per_meal_cost": float(report.per_meal_cost) if report.per_meal_cost else None,
        "breakdown": daily_data.get("breakdown", []),
        "expense_by_category": expense_by_category,
        "daily_breakdown": daily_data.get("daily_breakdown", []),
        "meals": {
            "breakfast": report.meals.breakfast,
            "lunch": report.meals.lunch,
            "dinner": report.meals.dinner,
        },
        "customers": {
            "total_enrolled": report.customers.total_enrolled,
            "active_this_period": report.customers.active_this_period,
        },
    }

# ─── Dining Router ────────────────────────────────────────────────────────────
dining_router = APIRouter(prefix="/dining", tags=["Dining"])


@dining_router.get("/schedules")
async def get_schedules(db: AsyncSession = Depends(get_db)):
    service = DiningService(db)
    schedules = await service.get_schedules()
    return {"success": True, "data": schedules}


@dining_router.put("/schedules/{meal_type}")
async def update_schedule(
    meal_type: str,
    data: MealScheduleUpdate,
    current_user: User = Depends(require_permission(Permission.MANAGE_MEAL_SCHEDULES)),
    db: AsyncSession = Depends(get_db),
):
    service = DiningService(db)
    schedule = await service.update_schedule(meal_type.upper(), data, current_user.id)
    return {"success": True, "data": schedule}


@dining_router.get("/menus")
async def get_menus(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = DiningService(db)
    if start_date and end_date:
        menus = await service.get_menus_range(start_date, end_date)
    else:
        menus = await service.get_menus_for_date(date.today())
    return {"success": True, "data": menus}


@dining_router.get("/menus/{menu_date}")
async def get_menus_for_date(menu_date: date, db: AsyncSession = Depends(get_db)):
    service = DiningService(db)
    menus = await service.get_menus_for_date(menu_date)
    return {"success": True, "data": menus}


@dining_router.post("/menus", status_code=201)
async def create_menu(
    data: DailyMenuCreate,
    current_user: User = Depends(require_permission(Permission.MANAGE_DAILY_MENUS)),
    db: AsyncSession = Depends(get_db),
):
    service = DiningService(db)
    menu = await service.create_menu(data, current_user.id)
    return {"success": True, "data": menu}


@dining_router.put("/menus/{menu_id}")
async def update_menu(
    menu_id: str,
    data: DailyMenuUpdate,
    current_user: User = Depends(require_permission(Permission.MANAGE_DAILY_MENUS)),
    db: AsyncSession = Depends(get_db),
):
    service = DiningService(db)
    menu = await service.update_menu(menu_id, data, current_user.id)
    return {"success": True, "data": menu}


@dining_router.patch("/menus/{menu_id}/cancel")
async def cancel_menu(
    menu_id: str,
    current_user: User = Depends(require_permission(Permission.MANAGE_DAILY_MENUS)),
    db: AsyncSession = Depends(get_db),
):
    service = DiningService(db)
    menu = await service.cancel_menu(menu_id, current_user.id)
    return {"success": True, "data": menu}


@dining_router.delete("/menus/{menu_id}")
async def delete_menu(
    menu_id: str,
    current_user: User = Depends(require_permission(Permission.MANAGE_DAILY_MENUS)),
    db: AsyncSession = Depends(get_db),
):
    service = DiningService(db)
    await service.delete_menu(menu_id)
    return {"success": True, "message": "Menu deleted"}


# ─── Customers Router ─────────────────────────────────────────────────────────
customers_router = APIRouter(prefix="/customers", tags=["Customers"])


@customers_router.get("")
async def list_customers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_permission(Permission.MANAGE_CUSTOMERS)),
    db: AsyncSession = Depends(get_db),
):
    service = DiningService(db)
    customers, total = await service.get_customers(page=page, per_page=per_page, search=search)
    from app.schemas.user import UserResponse
    from app.schemas.common import paginate
    return {
        "success": True,
        "data": [UserResponse.model_validate(c) for c in customers],
        "meta": paginate(page, per_page, total).__dict__,
    }


@customers_router.post("/{user_id}", status_code=201)
async def add_customer(
    user_id: str,
    current_user: User = Depends(require_permission(Permission.MANAGE_CUSTOMERS)),
    db: AsyncSession = Depends(get_db),
):
    service = DiningService(db)
    user = await service.add_customer(user_id, current_user.id)
    from app.schemas.user import UserResponse
    from app.repositories.meal_repo import AuditRepository
    audit = AuditRepository(db)
    await audit.log(user_id=current_user.id, action="CUSTOMER_ADDED", entity_type="User", entity_id=user_id)
    return {"success": True, "message": "Customer enrolled", "data": UserResponse.model_validate(user)}


@customers_router.delete("/{user_id}")
async def remove_customer(
    user_id: str,
    current_user: User = Depends(require_permission(Permission.MANAGE_CUSTOMERS)),
    db: AsyncSession = Depends(get_db),
):
    service = DiningService(db)
    user = await service.remove_customer(user_id, current_user.id)
    from app.repositories.meal_repo import AuditRepository
    audit = AuditRepository(db)
    await audit.log(user_id=current_user.id, action="CUSTOMER_REMOVED", entity_type="User", entity_id=user_id)
    return {"success": True, "message": "Customer removed"}


# ─── Meals Router ─────────────────────────────────────────────────────────────
meals_router = APIRouter(prefix="/meals", tags=["Meals"])


@meals_router.get("/today")
async def get_today_meals(
    current_user: User = Depends(require_roles(UserRole.CUSTOMER)),
    db: AsyncSession = Depends(get_db),
):
    service = MealService(db)
    statuses = await service.get_today_status(current_user.id)
    return {"success": True, "data": statuses}


@meals_router.post("", status_code=201)
async def add_meal(
    data: StudentMealCreate,
    current_user: User = Depends(require_roles(UserRole.CUSTOMER)),
    db: AsyncSession = Depends(get_db),
):
    service = MealService(db)
    meal = await service.add_meal(current_user.id, data.date, data.meal_type)
    from app.repositories.meal_repo import AuditRepository
    audit = AuditRepository(db)
    await audit.log(user_id=current_user.id, action="MEAL_ADDED", entity_type="StudentMeal", entity_id=meal.id)
    return {"success": True, "data": meal}


@meals_router.delete("/{meal_id}")
async def cancel_meal(
    meal_id: str,
    current_user: User = Depends(require_roles(UserRole.CUSTOMER)),
    db: AsyncSession = Depends(get_db),
):
    service = MealService(db)
    meal = await service.cancel_meal(current_user.id, meal_id)
    from app.repositories.meal_repo import AuditRepository
    audit = AuditRepository(db)
    await audit.log(user_id=current_user.id, action="MEAL_CANCELLED", entity_type="StudentMeal", entity_id=meal_id)
    return {"success": True, "data": meal}


@meals_router.get("/history")
async def get_meal_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2020),
    meal_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_roles(UserRole.CUSTOMER)),
    db: AsyncSession = Depends(get_db),
):
    service = MealService(db)
    meals, total = await service.get_history(
        current_user.id, page=page, per_page=per_page,
        month=month, year=year, meal_type=meal_type, status=status,
    )
    from app.schemas.common import paginate
    return {"success": True, "data": meals, "meta": paginate(page, per_page, total).__dict__}


@meals_router.get("/summary")
async def get_meal_summary(
    year: int = Query(..., ge=2020),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(require_roles(UserRole.CUSTOMER)),
    db: AsyncSession = Depends(get_db),
):
    service = MealService(db)
    summary = await service.get_monthly_summary(current_user.id, year, month)
    return {"success": True, "data": summary}


# ─── Requests Router ──────────────────────────────────────────────────────────
requests_router = APIRouter(prefix="/requests", tags=["Meal Requests"])


@requests_router.get("")
async def list_requests(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = MealRequestService(db)
    user_filter = None
    if current_user.role == UserRole.NON_CUSTOMER.value:
        user_filter = current_user.id
    requests, total = await service.get_requests(page=page, per_page=per_page, user_id=user_filter, status=status)
    from app.schemas.common import paginate
    return {
        "success": True,
        "data": [_request_dict(r) for r in requests],
        "meta": paginate(page, per_page, total).__dict__,
    }


@requests_router.post("", status_code=201)
async def create_request(
    data: MealRequestCreate,
    current_user: User = Depends(require_roles(UserRole.NON_CUSTOMER)),
    db: AsyncSession = Depends(get_db),
):
    service = MealRequestService(db)
    req = await service.create_request(current_user.id, data)
    return {"success": True, "data": _request_dict(req)}


@requests_router.post("/payment")
async def submit_payment(
    data: PaymentSubmit,
    current_user: User = Depends(require_roles(UserRole.NON_CUSTOMER)),
    db: AsyncSession = Depends(get_db),
):
    service = MealRequestService(db)
    req = await service.submit_payment(current_user.id, data)
    return {"success": True, "data": _request_dict(req)}


@requests_router.get("/{request_id}")
async def get_request(
    request_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories.meal_repo import MealRequestRepository
    from app.core.exceptions import NotFoundException, PermissionDeniedException
    repo = MealRequestRepository(db)
    request = await repo.get_by_id_with_relations(request_id)
    if not request:
        raise NotFoundException("MealRequest", request_id)
    is_manager = current_user.role in (UserRole.DINING_MANAGER.value, UserRole.PROVOST.value)
    if not is_manager and request.user_id != current_user.id:
        raise PermissionDeniedException()
    return {"success": True, "data": _request_dict(request)}


@requests_router.delete("/{request_id}")
async def cancel_request(
    request_id: str,
    current_user: User = Depends(require_roles(UserRole.NON_CUSTOMER)),
    db: AsyncSession = Depends(get_db),
):
    service = MealRequestService(db)
    req = await service.cancel_request(current_user.id, request_id)
    return {"success": True, "data": _request_dict(req)}


@requests_router.post("/{request_id}/payment", status_code=201)
async def submit_payment_for_request(
    request_id: str,
    data: PaymentCreate,
    current_user: User = Depends(require_roles(UserRole.NON_CUSTOMER)),
    db: AsyncSession = Depends(get_db),
):
    service = MealRequestService(db)
    req = await service.submit_payment_by_id(
        user_id=current_user.id,
        request_id=request_id,
        amount=data.amount,
        payment_method=data.payment_method,
        reference_no=data.transaction_id,
        note=data.note,
    )
    return {"success": True, "data": _request_dict(req)}


@requests_router.patch("/{request_id}/approve")
async def approve_request(
    request_id: str,
    current_user: User = Depends(require_permission(Permission.APPROVE_MEAL_REQUESTS)),
    db: AsyncSession = Depends(get_db),
):
    service = MealRequestService(db)
    req = await service.approve_request(request_id, current_user.id)
    from app.repositories.meal_repo import AuditRepository, MealRequestRepository
    audit = AuditRepository(db)
    await audit.log(user_id=current_user.id, action="REQUEST_APPROVED", entity_type="MealRequest", entity_id=request_id)
    full = await MealRequestRepository(db).get_by_id_with_relations(request_id)
    return {"success": True, "data": _request_dict(full or req)}


@requests_router.patch("/{request_id}/reject")
async def reject_request(
    request_id: str,
    data: MealRequestReview,
    current_user: User = Depends(require_permission(Permission.APPROVE_MEAL_REQUESTS)),
    db: AsyncSession = Depends(get_db),
):
    service = MealRequestService(db)
    req = await service.reject_request(request_id, current_user.id, data.rejection_note)
    from app.repositories.meal_repo import AuditRepository, MealRequestRepository
    audit = AuditRepository(db)
    await audit.log(user_id=current_user.id, action="REQUEST_REJECTED", entity_type="MealRequest", entity_id=request_id)
    full = await MealRequestRepository(db).get_by_id_with_relations(request_id)
    return {"success": True, "data": _request_dict(full or req)}


# ─── Expenses Router ──────────────────────────────────────────────────────────
expenses_router = APIRouter(prefix="/expenses", tags=["Expenses"])


@expenses_router.get("")
async def list_expenses(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission(Permission.MANAGE_EXPENSES)),
    db: AsyncSession = Depends(get_db),
):
    service = ExpenseService(db)
    expenses, total = await service.get_paginated(
        page=page, per_page=per_page, category=category, start_date=start_date, end_date=end_date
    )
    from app.schemas.common import paginate
    return {
        "success": True,
        "data": [_expense_dict(e) for e in expenses],
        "meta": paginate(page, per_page, total).__dict__,
    }


@expenses_router.get("/{expense_id}")
async def get_expense(
    expense_id: str,
    current_user: User = Depends(require_permission(Permission.MANAGE_EXPENSES)),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories.meal_repo import ExpenseRepository
    from app.core.exceptions import NotFoundException
    repo = ExpenseRepository(db)
    expense = await repo.get_by_id(expense_id)
    if not expense:
        raise NotFoundException("Expense", expense_id)
    return {"success": True, "data": _expense_dict(expense)}


@expenses_router.post("", status_code=201)
async def create_expense(
    data: ExpenseCreate,
    current_user: User = Depends(require_permission(Permission.MANAGE_EXPENSES)),
    db: AsyncSession = Depends(get_db),
):
    service = ExpenseService(db)
    expense = await service.create(data, current_user.id)
    from app.repositories.meal_repo import AuditRepository
    audit = AuditRepository(db)
    await audit.log(user_id=current_user.id, action="EXPENSE_CREATED", entity_type="Expense", entity_id=expense.id)
    return {"success": True, "data": _expense_dict(expense)}


@expenses_router.put("/{expense_id}")
async def update_expense(
    expense_id: str,
    data: ExpenseUpdate,
    current_user: User = Depends(require_permission(Permission.MANAGE_EXPENSES)),
    db: AsyncSession = Depends(get_db),
):
    service = ExpenseService(db)
    expense = await service.update(expense_id, data, current_user.id)
    return {"success": True, "data": _expense_dict(expense)}


@expenses_router.delete("/{expense_id}")
async def delete_expense(
    expense_id: str,
    current_user: User = Depends(require_permission(Permission.MANAGE_EXPENSES)),
    db: AsyncSession = Depends(get_db),
):
    service = ExpenseService(db)
    await service.delete(expense_id)
    from app.repositories.meal_repo import AuditRepository
    audit = AuditRepository(db)
    await audit.log(user_id=current_user.id, action="EXPENSE_DELETED", entity_type="Expense", entity_id=expense_id)
    return {"success": True, "message": "Expense deleted"}


# ─── Reports Router ───────────────────────────────────────────────────────────
reports_router = APIRouter(prefix="/reports", tags=["Reports"])


@reports_router.get("/daily")
async def daily_report(
    report_date: date = Query(default_factory=date.today),
    current_user: User = Depends(require_permission(Permission.VIEW_FINANCIAL_REPORTS)),
    db: AsyncSession = Depends(get_db),
):
    service = ReportService(db)
    report = await service.generate(report_date, report_date)
    daily_data = await service.get_daily_breakdown(report_date, report_date)
    return {"success": True, "data": _format_report(report, daily_data)}


@reports_router.get("/weekly")
async def weekly_report(
    year: int = Query(..., ge=2020),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(require_permission(Permission.VIEW_FINANCIAL_REPORTS)),
    db: AsyncSession = Depends(get_db),
):
    start = date(year, month, 1)
    end = start + timedelta(days=6)
    service = ReportService(db)
    report = await service.generate(start, end)
    daily_data = await service.get_daily_breakdown(start, end)
    return {"success": True, "data": _format_report(report, daily_data)}


@reports_router.get("/monthly")
async def monthly_report(
    year: int = Query(..., ge=2020),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(require_permission(Permission.VIEW_FINANCIAL_REPORTS)),
    db: AsyncSession = Depends(get_db),
):
    from calendar import monthrange
    _, last_day = monthrange(year, month)
    start = date(year, month, 1)
    end = date(year, month, last_day)
    service = ReportService(db)
    report = await service.generate(start, end)
    daily_data = await service.get_daily_breakdown(start, end)
    return {"success": True, "data": _format_report(report, daily_data)}


@reports_router.get("/yearly")
async def yearly_report(
    year: int = Query(..., ge=2020),
    current_user: User = Depends(require_permission(Permission.VIEW_FINANCIAL_REPORTS)),
    db: AsyncSession = Depends(get_db),
):
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    service = ReportService(db)
    report = await service.generate(start, end)
    daily_data = await service.get_daily_breakdown(start, end)
    return {"success": True, "data": _format_report(report, daily_data)}


@reports_router.get("/export")
async def export_report(
    period: str = Query("monthly"),
    year: int = Query(..., ge=2020),
    month: int = Query(1, ge=1, le=12),
    current_user: User = Depends(require_permission(Permission.VIEW_FINANCIAL_REPORTS)),
    db: AsyncSession = Depends(get_db),
):
    from calendar import monthrange
    if period == "daily":
        start = end = date(year, month, 1)
    elif period == "weekly":
        start = date(year, month, 1)
        end = start + timedelta(days=6)
    elif period == "yearly":
        start, end = date(year, 1, 1), date(year, 12, 31)
    else:
        _, last_day = monthrange(year, month)
        start, end = date(year, month, 1), date(year, month, last_day)

    service = ReportService(db)
    report = await service.generate(start, end)
    daily_data = await service.get_daily_breakdown(start, end)
    data = _format_report(report, daily_data)

    lines = [
        "Period,Total Income,Total Expense,Net,Total Meals",
        f"{data['period_start']} to {data['period_end']},{data['total_income']},{data['total_expense']},{data['net']},{data['total_meals']}",
        "",
        "Date,Income,Expense",
    ]
    for row in data.get("breakdown", []):
        lines.append(f"{row['period']},{row['income']},{row['expense']}")

    csv_content = "\n".join(lines)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=report_{period}_{year}_{month}.csv"},
    )


# ─── Audit Router ─────────────────────────────────────────────────────────────
audit_router = APIRouter(prefix="/audit", tags=["Audit Logs"])


@audit_router.get("")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(require_roles(UserRole.PROVOST)),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories.meal_repo import AuditRepository
    from app.models.expense import AuditLog
    from sqlalchemy import select, func, and_
    from sqlalchemy.orm import selectinload

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

    q = select(AuditLog).options(selectinload(AuditLog.user))
    cq = select(func.count()).select_from(AuditLog)
    if conditions:
        q = q.where(and_(*conditions))
        cq = cq.where(and_(*conditions))

    total = (await db.execute(cq)).scalar() or 0
    offset = (page - 1) * per_page
    logs = (await db.execute(q.order_by(AuditLog.created_at.desc()).offset(offset).limit(per_page))).scalars().all()

    from app.schemas.common import paginate
    return {"success": True, "data": [_audit_dict(l) for l in logs], "meta": paginate(page, per_page, total).__dict__}


@audit_router.get("/recent")
async def recent_audit_logs(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(require_roles(UserRole.PROVOST)),
    db: AsyncSession = Depends(get_db),
):
    from app.models.expense import AuditLog
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    logs = (await db.execute(
        select(AuditLog).options(selectinload(AuditLog.user))
        .order_by(AuditLog.created_at.desc()).limit(limit)
    )).scalars().all()
    return {"success": True, "data": [_audit_dict(l) for l in logs]}


@audit_router.get("/{log_id}")
async def get_audit_log(
    log_id: int,
    current_user: User = Depends(require_roles(UserRole.PROVOST)),
    db: AsyncSession = Depends(get_db),
):
    from app.models.expense import AuditLog
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.core.exceptions import NotFoundException
    log = (await db.execute(
        select(AuditLog).options(selectinload(AuditLog.user)).where(AuditLog.id == log_id)
    )).scalars().first()
    if not log:
        raise NotFoundException("AuditLog", str(log_id))
    return {"success": True, "data": _audit_dict(log)}


# ─── Earnings Router ─────────────────────────────────────────────────────────
earnings_router = APIRouter(prefix="/earnings", tags=["Earnings"])


@earnings_router.get("")
async def list_earnings(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission(Permission.MANAGE_EARNINGS)),
    db: AsyncSession = Depends(get_db),
):
    service = EarningService(db)
    earnings, total = await service.get_paginated(
        page=page, per_page=per_page, category=category, start_date=start_date, end_date=end_date
    )
    from app.schemas.common import paginate
    return {
        "success": True,
        "data": [_earning_dict(e) for e in earnings],
        "meta": paginate(page, per_page, total).__dict__,
    }


@earnings_router.get("/{earning_id}")
async def get_earning(
    earning_id: str,
    current_user: User = Depends(require_permission(Permission.MANAGE_EARNINGS)),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories.meal_repo import EarningRepository
    from app.core.exceptions import NotFoundException
    repo = EarningRepository(db)
    earning = await repo.get_by_id(earning_id)
    if not earning:
        raise NotFoundException("Earning", earning_id)
    return {"success": True, "data": _earning_dict(earning)}


@earnings_router.post("", status_code=201)
async def create_earning(
    data: EarningCreate,
    current_user: User = Depends(require_permission(Permission.MANAGE_EARNINGS)),
    db: AsyncSession = Depends(get_db),
):
    service = EarningService(db)
    earning = await service.create(data, current_user.id)
    from app.repositories.meal_repo import AuditRepository
    audit = AuditRepository(db)
    await audit.log(user_id=current_user.id, action="EARNING_CREATED", entity_type="Earning", entity_id=earning.id)
    return {"success": True, "data": _earning_dict(earning)}


@earnings_router.put("/{earning_id}")
async def update_earning(
    earning_id: str,
    data: EarningUpdate,
    current_user: User = Depends(require_permission(Permission.MANAGE_EARNINGS)),
    db: AsyncSession = Depends(get_db),
):
    service = EarningService(db)
    earning = await service.update(earning_id, data, current_user.id)
    return {"success": True, "data": _earning_dict(earning)}


@earnings_router.delete("/{earning_id}")
async def delete_earning(
    earning_id: str,
    current_user: User = Depends(require_permission(Permission.MANAGE_EARNINGS)),
    db: AsyncSession = Depends(get_db),
):
    service = EarningService(db)
    await service.delete(earning_id)
    from app.repositories.meal_repo import AuditRepository
    audit = AuditRepository(db)
    await audit.log(user_id=current_user.id, action="EARNING_DELETED", entity_type="Earning", entity_id=earning_id)
    return {"success": True, "message": "Earning deleted"}


# ─── Dashboard Router ────────────────────────────────────────────────────────
dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@dashboard_router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = DashboardService(db)
    stats = await service.get_stats()
    return {
        "success": True,
        "data": {
            "total_expenses": float(stats.total_expenses),
            "total_earnings": float(stats.total_earnings),
            "net_balance": float(stats.net_balance),
            "active_customers": stats.active_customers,
            "session": {
                "start_date": str(stats.session.start_date),
                "end_date": str(stats.session.end_date),
                "total_possible_meals": stats.session.total_possible_meals,
                "consumed_meals": stats.session.consumed_meals,
                "remaining_meals": stats.session.remaining_meals,
                "per_meal_cost": float(stats.session.per_meal_cost) if stats.session.per_meal_cost else 0,
                "remaining_cost": float(stats.session.remaining_cost) if stats.session.remaining_cost else 0,
            },
        },
    }


# ─── Serialization helpers for payments ──────────────────────────────────────

def _member_payment_dict(mp) -> dict:
    try:
        user = mp.user
    except Exception:
        user = None
    return {
        "id": mp.id,
        "user_id": mp.user_id,
        "year": mp.year,
        "month": mp.month,
        "amount_due": float(mp.amount_due),
        "amount_paid": float(mp.amount_paid),
        "status": mp.status,
        "created_at": mp.created_at.isoformat(),
        "updated_at": mp.updated_at.isoformat(),
        "user": _user_dict(user),
    }


def _proof_dict(proof) -> dict:
    try:
        user = proof.user
    except Exception:
        user = None
    return {
        "id": proof.id,
        "member_payment_id": proof.member_payment_id,
        "user_id": proof.user_id,
        "proof_type": proof.proof_type,
        "proof_value": proof.proof_value,
        "status": proof.status,
        "reviewed_by": proof.reviewed_by,
        "reviewed_at": proof.reviewed_at.isoformat() if proof.reviewed_at else None,
        "rejection_note": proof.rejection_note,
        "created_at": proof.created_at.isoformat(),
        "user": _user_dict(user),
    }


# ─── Member Payments Router ─────────────────────────────────────────────────
member_payments_router = APIRouter(prefix="/member-payments", tags=["Member Payments"])


@member_payments_router.get("")
async def list_member_payments(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = MemberPaymentService(db)
    is_manager = current_user.role in ("PROVOST", "DINING_MANAGER")
    if not is_manager:
        payments, total = await service.get_paginated(
            page=page, per_page=per_page, status=status, year=year, month=month
        )
        payments = [p for p in payments if p.user_id == current_user.id]
        total = len(payments)
    else:
        payments, total = await service.get_paginated(
            page=page, per_page=per_page, status=status, year=year, month=month
        )
    from app.schemas.common import paginate
    return {
        "success": True,
        "data": [_member_payment_dict(p) for p in payments],
        "meta": paginate(page, per_page, total).__dict__,
    }


@member_payments_router.get("/summary")
async def payment_summary(
    year: int = Query(..., ge=2020),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(require_permission(Permission.MANAGE_MEMBER_PAYMENTS)),
    db: AsyncSession = Depends(get_db),
):
    service = MemberPaymentService(db)
    summary = await service.get_summary(year, month)
    return {"success": True, "data": summary}


@member_payments_router.post("/init", status_code=201)
async def init_month_payments(
    year: int = Query(..., ge=2020),
    month: int = Query(..., ge=1, le=12),
    amount_due: float = Query(0),
    current_user: User = Depends(require_permission(Permission.MANAGE_MEMBER_PAYMENTS)),
    db: AsyncSession = Depends(get_db),
):
    from decimal import Decimal
    service = MemberPaymentService(db)
    created = await service.init_month_for_active_customers(year, month, Decimal(str(amount_due)))
    return {"success": True, "message": f"Initialized {created} payment records", "data": {"created": created}}


@member_payments_router.patch("/{payment_id}/mark-paid")
async def mark_payment_paid(
    payment_id: str,
    current_user: User = Depends(require_permission(Permission.MANAGE_MEMBER_PAYMENTS)),
    db: AsyncSession = Depends(get_db),
):
    service = MemberPaymentService(db)
    payment = await service.mark_paid(payment_id)
    return {"success": True, "data": _member_payment_dict(payment)}


@member_payments_router.patch("/{payment_id}/mark-pending")
async def mark_payment_pending(
    payment_id: str,
    current_user: User = Depends(require_permission(Permission.MANAGE_MEMBER_PAYMENTS)),
    db: AsyncSession = Depends(get_db),
):
    service = MemberPaymentService(db)
    payment = await service.mark_pending(payment_id)
    return {"success": True, "data": _member_payment_dict(payment)}


@member_payments_router.patch("/{payment_id}/toggle-active")
async def toggle_user_active(
    payment_id: str,
    current_user: User = Depends(require_permission(Permission.TOGGLE_USER_STATUS)),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories.user_repo import UserRepository
    from app.core.exceptions import NotFoundException
    repo = UserRepository(db)
    from app.repositories.meal_repo import MemberPaymentRepository
    mp_repo = MemberPaymentRepository(db)
    payment = await mp_repo.get_by_id(payment_id)
    if not payment:
        raise NotFoundException("MemberPayment", payment_id)
    user = await repo.get_by_id(payment.user_id)
    if not user:
        raise NotFoundException("User", payment.user_id)
    new_status = "INACTIVE" if user.status == "ACTIVE" else "ACTIVE"
    await repo.update(user, {"status": new_status})
    return {"success": True, "message": f"User is now {new_status}", "data": {"status": new_status}}


# ─── Payment Proofs Router ──────────────────────────────────────────────────
payment_proofs_router = APIRouter(prefix="/payment-proofs", tags=["Payment Proofs"])


@payment_proofs_router.get("")
async def list_proofs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = MemberPaymentService(db)
    is_manager = current_user.role in ("PROVOST", "DINING_MANAGER")
    user_id = None if is_manager else current_user.id
    proofs, total = await service.get_proofs(page=page, per_page=per_page, status=status, user_id=user_id)
    from app.schemas.common import paginate
    return {
        "success": True,
        "data": [_proof_dict(p) for p in proofs],
        "meta": paginate(page, per_page, total).__dict__,
    }


@payment_proofs_router.post("", status_code=201)
async def submit_proof(
    data: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = MemberPaymentService(db)
    proof = await service.submit_proof(
        user_id=current_user.id,
        member_payment_id=data["member_payment_id"],
        proof_type=data["proof_type"],
        proof_value=data["proof_value"],
    )
    return {"success": True, "data": _proof_dict(proof)}


@payment_proofs_router.patch("/{proof_id}/approve")
async def approve_proof(
    proof_id: str,
    current_user: User = Depends(require_permission(Permission.MANAGE_MEMBER_PAYMENTS)),
    db: AsyncSession = Depends(get_db),
):
    service = MemberPaymentService(db)
    proof = await service.approve_proof(proof_id, current_user.id)
    return {"success": True, "data": _proof_dict(proof)}


@payment_proofs_router.patch("/{proof_id}/reject")
async def reject_proof(
    proof_id: str,
    data: dict = {},
    current_user: User = Depends(require_permission(Permission.MANAGE_MEMBER_PAYMENTS)),
    db: AsyncSession = Depends(get_db),
):
    service = MemberPaymentService(db)
    proof = await service.reject_proof(proof_id, current_user.id, data.get("rejection_note"))
    return {"success": True, "data": _proof_dict(proof)}
