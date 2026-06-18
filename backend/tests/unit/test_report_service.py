"""Unit tests for ReportService — income, expense, and meal breakdown."""
import pytest
import pytest_asyncio
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense, MealRequest, Payment
from app.models.meal import StudentMeal
from app.models.user import User


pytestmark = pytest.mark.asyncio


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def report_data(
    db: AsyncSession,
    customer_user: User,
    manager_user: User,
    noncustomer_user: User,
) -> dict:
    """Seed a fixed set of data for deterministic report testing."""
    today = date.today()
    d = today - timedelta(days=1)

    # 3 meals for customer
    for mt in ("BREAKFAST", "LUNCH", "DINNER"):
        db.add(StudentMeal(user_id=str(customer_user.id), date=d, meal_type=mt, status="ACTIVE"))

    # 1 cancelled meal
    db.add(StudentMeal(
        user_id=str(customer_user.id),
        date=d - timedelta(days=1),
        meal_type="LUNCH",
        status="CANCELLED",
    ))

    # 2 expenses
    exp1 = Expense(
        name="Rice Purchase",
        category="FOOD_PURCHASE",
        amount=Decimal("5000.00"),
        expense_date=d,
        created_by=str(manager_user.id),
    )
    exp2 = Expense(
        name="Gas Bill",
        category="UTILITIES",
        amount=Decimal("2000.00"),
        expense_date=d,
        created_by=str(manager_user.id),
    )
    db.add(exp1)
    db.add(exp2)

    # 1 completed payment from non-customer request
    payment = Payment(
        user_id=str(noncustomer_user.id),
        amount=Decimal("80.00"),
        payment_method="CASH",
        status="COMPLETED",
    )
    db.add(payment)
    await db.flush()

    request = MealRequest(
        user_id=str(noncustomer_user.id),
        date=d,
        meal_type="LUNCH",
        status="APPROVED",
        payment_id=str(payment.id),
        reviewed_by=str(manager_user.id),
    )
    db.add(request)
    await db.flush()

    return {
        "date": d,
        "expected_meals": 3,
        "expected_expenses": Decimal("7000.00"),
        "expected_income": Decimal("80.00"),
    }


# ─── Report generation ────────────────────────────────────────────────────────

class TestReportGeneration:
    async def test_expense_sum_correct(self, db: AsyncSession, report_data: dict, manager_user: User):
        from app.repositories.meal_repo import ExpenseRepository
        repo = ExpenseRepository(db)

        d = report_data["date"]
        total = await repo.sum_in_range(start_date=d, end_date=d)
        assert total >= report_data["expected_expenses"]

    async def test_expense_by_category(self, db: AsyncSession, report_data: dict, manager_user: User):
        from app.repositories.meal_repo import ExpenseRepository
        repo = ExpenseRepository(db)

        d = report_data["date"]
        by_category = await repo.sum_by_category(start_date=d, end_date=d)
        assert "FOOD_PURCHASE" in by_category
        assert "UTILITIES" in by_category
        assert by_category["FOOD_PURCHASE"] >= Decimal("5000.00")
        assert by_category["UTILITIES"] >= Decimal("2000.00")

    async def test_active_meals_counted(self, db: AsyncSession, report_data: dict, customer_user: User):
        from app.repositories.meal_repo import StudentMealRepository
        repo = StudentMealRepository(db)

        d = report_data["date"]
        count = await repo.count_served(date_from=d, date_to=d)
        assert count >= report_data["expected_meals"]

    async def test_net_is_income_minus_expenses(self, report_data: dict):
        income = report_data["expected_income"]
        expenses = report_data["expected_expenses"]
        net = income - expenses
        assert net == Decimal("-6920.00")  # 80 - 7000

    async def test_per_meal_cost(self, report_data: dict):
        expenses = report_data["expected_expenses"]
        meals = report_data["expected_meals"]
        per_meal = expenses / meals
        assert round(per_meal, 2) == Decimal("2333.33")


# ─── Date utilities ───────────────────────────────────────────────────────────

class TestDateUtilities:
    def test_start_of_month(self):
        from app.utils.date_utils import start_of_month
        d = start_of_month(2024, 6)
        assert d.day == 1
        assert d.month == 6
        assert d.year == 2024

    def test_end_of_month(self):
        from app.utils.date_utils import end_of_month
        d = end_of_month(2024, 2)  # Leap year
        assert d.day == 29  # 2024 is a leap year
        d2 = end_of_month(2023, 2)
        assert d2.day == 28

    def test_week_bounds_monday_sunday(self):
        from app.utils.date_utils import get_week_bounds
        wednesday = date(2024, 6, 5)  # A Wednesday
        monday, sunday = get_week_bounds(wednesday)
        assert monday.weekday() == 0  # Monday
        assert sunday.weekday() == 6  # Sunday
        assert (sunday - monday).days == 6

    def test_days_in_month(self):
        from app.utils.date_utils import days_in_month
        assert days_in_month(2024, 2) == 29
        assert days_in_month(2023, 2) == 28
        assert days_in_month(2024, 1) == 31
        assert days_in_month(2024, 4) == 30

    def test_format_date(self):
        from app.utils.date_utils import format_date
        d = date(2024, 6, 15)
        assert format_date(d) == "2024-06-15"
