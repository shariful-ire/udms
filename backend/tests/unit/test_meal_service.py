"""Unit tests for MealService — add, cancel, deadline enforcement."""
import pytest
import pytest_asyncio
from datetime import date, datetime, time, timedelta, timezone
from unittest.mock import patch

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meal import MealSchedule, StudentMeal
from app.models.user import User


pytestmark = pytest.mark.asyncio
UTC = timezone.utc


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def breakfast_schedule(db: AsyncSession, manager_user: User) -> MealSchedule:
    schedule = MealSchedule(
        meal_type="BREAKFAST",
        start_time=time(7, 0),
        end_time=time(9, 0),
        cancel_deadline=time(6, 30),
        is_active=True,
        created_by=str(manager_user.id),
    )
    db.add(schedule)
    await db.flush()
    return schedule


@pytest_asyncio.fixture
async def lunch_schedule(db: AsyncSession, manager_user: User) -> MealSchedule:
    schedule = MealSchedule(
        meal_type="LUNCH",
        start_time=time(12, 0),
        end_time=time(14, 0),
        cancel_deadline=time(11, 30),
        is_active=True,
        created_by=str(manager_user.id),
    )
    db.add(schedule)
    await db.flush()
    return schedule


# ─── MealSchedule model ───────────────────────────────────────────────────────

class TestMealScheduleModel:
    async def test_schedule_created_correctly(self, breakfast_schedule: MealSchedule):
        assert breakfast_schedule.meal_type == "BREAKFAST"
        assert breakfast_schedule.start_time == time(7, 0)
        assert breakfast_schedule.end_time == time(9, 0)
        assert breakfast_schedule.cancel_deadline == time(6, 30)
        assert breakfast_schedule.is_active is True

    async def test_inactive_schedule_can_be_set(self, db: AsyncSession, breakfast_schedule: MealSchedule):
        breakfast_schedule.is_active = False
        db.add(breakfast_schedule)
        await db.flush()
        assert breakfast_schedule.is_active is False


# ─── StudentMeal model ────────────────────────────────────────────────────────

class TestStudentMealModel:
    async def test_create_active_meal(
        self, db: AsyncSession, customer_user: User
    ):
        meal = StudentMeal(
            user_id=str(customer_user.id),
            date=date.today(),
            meal_type="LUNCH",
            status="ACTIVE",
        )
        db.add(meal)
        await db.flush()
        assert meal.status == "ACTIVE"
        assert meal.cancelled_at is None

    async def test_cancel_meal(self, db: AsyncSession, customer_user: User):
        meal = StudentMeal(
            user_id=str(customer_user.id),
            date=date.today(),
            meal_type="DINNER",
            status="ACTIVE",
        )
        db.add(meal)
        await db.flush()

        # Cancel it
        meal.status = "CANCELLED"
        meal.cancelled_at = datetime.now(UTC)
        db.add(meal)
        await db.flush()

        assert meal.status == "CANCELLED"
        assert meal.cancelled_at is not None

    async def test_unique_constraint_prevents_duplicate(
        self, db: AsyncSession, customer_user: User
    ):
        """Adding the same meal type for same user+date should fail."""
        d = date.today() - timedelta(days=1)
        meal1 = StudentMeal(user_id=str(customer_user.id), date=d, meal_type="BREAKFAST", status="ACTIVE")
        db.add(meal1)
        await db.flush()

        meal2 = StudentMeal(user_id=str(customer_user.id), date=d, meal_type="BREAKFAST", status="ACTIVE")
        db.add(meal2)
        with pytest.raises(Exception):  # IntegrityError from UNIQUE constraint
            await db.flush()


# ─── Deadline logic ───────────────────────────────────────────────────────────

class TestDeadlineLogic:
    def test_before_deadline_is_within_time(self):
        from app.utils.date_utils import is_past_deadline
        # Use a deadline far in the future (23:59)
        future_deadline = time(23, 59)
        assert not is_past_deadline(future_deadline)

    def test_after_deadline_is_past(self):
        from app.utils.date_utils import is_past_deadline
        # Use a deadline that has long passed (00:01)
        past_deadline = time(0, 1)
        assert is_past_deadline(past_deadline)

    def test_date_range_generation(self):
        from app.utils.date_utils import date_range
        start = date(2024, 1, 1)
        end = date(2024, 1, 5)
        days = list(date_range(start, end))
        assert len(days) == 5
        assert days[0] == start
        assert days[-1] == end


# ─── Meal repository ──────────────────────────────────────────────────────────

class TestMealRepository:
    async def test_count_meals_served_on_date(
        self, db: AsyncSession, customer_user: User
    ):
        from app.repositories.meal_repo import StudentMealRepository
        repo = StudentMealRepository(db)

        d = date(2024, 6, 15)
        for meal_type in ("BREAKFAST", "LUNCH"):
            db.add(StudentMeal(user_id=str(customer_user.id), date=d, meal_type=meal_type, status="ACTIVE"))
        await db.flush()

        count = await repo.count_served(date_from=d, date_to=d)
        assert count >= 2

    async def test_user_history_returns_correct_meals(
        self, db: AsyncSession, customer_user: User
    ):
        from app.repositories.meal_repo import StudentMealRepository
        repo = StudentMealRepository(db)

        d = date(2024, 6, 16)
        db.add(StudentMeal(user_id=str(customer_user.id), date=d, meal_type="DINNER", status="ACTIVE"))
        await db.flush()

        meals, total = await repo.get_user_history(
            user_id=str(customer_user.id),
            page=1,
            per_page=50,
        )
        assert total >= 1
        assert any(m.meal_type == "DINNER" and m.date == d for m in meals)
