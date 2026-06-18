from datetime import date, datetime, timezone
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictException,
    CustomerAlreadyExistsException,
    NotFoundException,
    NotACustomerException,
    PermissionDeniedException,
    ValidationException,
)
from app.models.meal import DailyMenu, MealSchedule, MenuItem, StudentMeal
from app.models.user import User
from app.repositories.meal_repo import DailyMenuRepository, MealScheduleRepository, StudentMealRepository
from app.repositories.user_repo import UserRepository
from app.schemas.meal import (
    DailyMenuCreate,
    DailyMenuResponse,
    DailyMenuUpdate,
    MealScheduleResponse,
    MealScheduleUpdate,
)


class DiningService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.schedule_repo = MealScheduleRepository(db)
        self.menu_repo = DailyMenuRepository(db)
        self.meal_repo = StudentMealRepository(db)
        self.user_repo = UserRepository(db)

    # ─── Meal Schedules ───────────────────────────────────────────────────────
    async def get_schedules(self) -> List[MealSchedule]:
        return await self.schedule_repo.get_all_schedules()

    async def update_schedule(
        self, meal_type: str, data: MealScheduleUpdate, updated_by: str
    ) -> MealSchedule:
        schedule = await self.schedule_repo.get_by_meal_type(meal_type)
        if not schedule:
            # Create if doesn't exist with defaults
            raise NotFoundException("MealSchedule", meal_type)

        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        update_data["updated_by"] = updated_by

        # Validate time order
        start = update_data.get("start_time", schedule.start_time)
        end = update_data.get("end_time", schedule.end_time)
        deadline = update_data.get("cancel_deadline", schedule.cancel_deadline)

        if start >= end:
            raise ValidationException("Start time must be before end time")
        if deadline >= start:
            raise ValidationException("Cancel deadline must be before start time")

        return await self.schedule_repo.update(schedule, update_data)

    async def create_default_schedules(self, created_by: str) -> None:
        """Initialize default meal schedules if none exist."""
        from datetime import time
        defaults = [
            {
                "meal_type": "BREAKFAST",
                "start_time": time(7, 0),
                "end_time": time(9, 0),
                "cancel_deadline": time(6, 30),
                "is_active": True,
                "created_by": created_by,
            },
            {
                "meal_type": "LUNCH",
                "start_time": time(12, 0),
                "end_time": time(14, 0),
                "cancel_deadline": time(11, 30),
                "is_active": True,
                "created_by": created_by,
            },
            {
                "meal_type": "DINNER",
                "start_time": time(19, 0),
                "end_time": time(21, 0),
                "cancel_deadline": time(18, 30),
                "is_active": True,
                "created_by": created_by,
            },
        ]
        for d in defaults:
            existing = await self.schedule_repo.get_by_meal_type(d["meal_type"])
            if not existing:
                await self.schedule_repo.create(d)

    # ─── Daily Menus ──────────────────────────────────────────────────────────
    async def create_menu(self, data: DailyMenuCreate, created_by: str) -> DailyMenu:
        existing = await self.menu_repo.get_by_date_and_type(data.date, data.meal_type)
        if existing:
            raise ConflictException(f"Menu for {data.meal_type} on {data.date} already exists")

        menu = await self.menu_repo.create({
            "date": data.date,
            "meal_type": data.meal_type,
            "is_cancelled": False,
            "created_by": created_by,
        })

        for item_data in data.items:
            from sqlalchemy import insert
            from app.models.meal import MenuItem
            mi = MenuItem(
                menu_id=menu.id,
                food_name=item_data.food_name,
                quantity=item_data.quantity,
                notes=item_data.notes,
            )
            self.db.add(mi)

        await self.db.flush()
        await self.db.refresh(menu)

        # Eagerly load items
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        result = await self.db.execute(
            select(DailyMenu)
            .options(selectinload(DailyMenu.items))
            .where(DailyMenu.id == menu.id)
        )
        return result.scalars().first()

    async def update_menu(self, menu_id: str, data: DailyMenuUpdate, updated_by: str) -> DailyMenu:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        result = await self.db.execute(
            select(DailyMenu).options(selectinload(DailyMenu.items)).where(DailyMenu.id == menu_id)
        )
        menu = result.scalars().first()
        if not menu:
            raise NotFoundException("DailyMenu", menu_id)

        if data.is_cancelled is not None:
            menu.is_cancelled = data.is_cancelled

        if data.items is not None:
            # Replace all items
            from sqlalchemy import delete
            await self.db.execute(
                delete(MenuItem).where(MenuItem.menu_id == menu_id)
            )
            for item_data in data.items:
                mi = MenuItem(
                    menu_id=menu_id,
                    food_name=item_data.food_name,
                    quantity=item_data.quantity,
                    notes=item_data.notes,
                )
                self.db.add(mi)

        menu.updated_by = updated_by
        self.db.add(menu)
        await self.db.flush()

        result = await self.db.execute(
            select(DailyMenu).options(selectinload(DailyMenu.items)).where(DailyMenu.id == menu_id)
        )
        return result.scalars().first()

    async def cancel_menu(self, menu_id: str, updated_by: str) -> DailyMenu:
        menu = await self.menu_repo.get_by_id(menu_id)
        if not menu:
            raise NotFoundException("DailyMenu", menu_id)
        return await self.menu_repo.update(menu, {"is_cancelled": True, "updated_by": updated_by})

    async def delete_menu(self, menu_id: str) -> bool:
        menu = await self.menu_repo.get_by_id(menu_id)
        if not menu:
            raise NotFoundException("DailyMenu", menu_id)
        return await self.menu_repo.delete(menu)

    async def get_menus_for_date(self, menu_date: date) -> List[DailyMenu]:
        return await self.menu_repo.get_by_date(menu_date)

    async def get_menus_range(self, start: date, end: date) -> List[DailyMenu]:
        return await self.menu_repo.get_range(start, end)

    # ─── Customer Management ──────────────────────────────────────────────────
    async def get_customers(
        self, *, page: int = 1, per_page: int = 20, search: Optional[str] = None
    ):
        users, total = await self.user_repo.get_paginated(
            page=page,
            per_page=per_page,
            search=search,
            role="CUSTOMER",
        )
        return users, total

    async def add_customer(self, user_id: str, manager_id: str) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        if user.role == "CUSTOMER":
            raise CustomerAlreadyExistsException()
        if user.role in ("PROVOST", "DINING_MANAGER"):
            raise PermissionDeniedException("Cannot enroll admin users as customers")

        return await self.user_repo.update(user, {"role": "CUSTOMER"})

    async def remove_customer(self, user_id: str, manager_id: str) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        if user.role != "CUSTOMER":
            raise NotACustomerException()

        return await self.user_repo.update(user, {"role": "NON_CUSTOMER"})
