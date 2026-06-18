"""Integration tests for dining endpoints."""
import pytest
from datetime import date, timedelta
from httpx import AsyncClient

from app.models.meal import MealSchedule
from app.models.user import User


pytestmark = pytest.mark.asyncio


class TestMealScheduleEndpoints:
    async def test_get_schedules_returns_list(self, client: AsyncClient, customer_user: User):
        from tests.conftest import make_access_token
        token = make_access_token(customer_user)
        response = await client.get(
            "/api/v1/dining/schedules",
            headers={"Authorization": f"Bearer {token}"},
        )
        # Schedules may be empty in test env, but endpoint should respond
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    async def test_update_schedule_requires_manager(self, client: AsyncClient, customer_user: User):
        """A regular customer should not be able to update schedules."""
        from tests.conftest import make_access_token
        token = make_access_token(customer_user)
        response = await client.put(
            "/api/v1/dining/schedules/BREAKFAST",
            headers={"Authorization": f"Bearer {token}"},
            json={"start_time": "07:30", "end_time": "09:30", "cancel_deadline": "07:00"},
        )
        assert response.status_code == 403

    async def test_update_schedule_as_manager(self, client: AsyncClient, manager_user: User):
        from tests.conftest import make_access_token
        token = make_access_token(manager_user)
        response = await client.put(
            "/api/v1/dining/schedules/BREAKFAST",
            headers={"Authorization": f"Bearer {token}"},
            json={"start_time": "07:30", "end_time": "09:30", "cancel_deadline": "07:00", "is_active": True},
        )
        assert response.status_code in (200, 404)  # 404 if no schedule yet


class TestDailyMenuEndpoints:
    async def test_get_menus_for_date(self, client: AsyncClient, customer_user: User):
        from tests.conftest import make_access_token
        token = make_access_token(customer_user)
        today = date.today().isoformat()
        response = await client.get(
            f"/api/v1/dining/menus/{today}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code in (200, 404)

    async def test_create_menu_as_manager(self, client: AsyncClient, manager_user: User):
        from tests.conftest import make_access_token
        token = make_access_token(manager_user)
        future_date = (date.today() + timedelta(days=10)).isoformat()
        response = await client.post(
            "/api/v1/dining/menus",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "date": future_date,
                "meal_type": "BREAKFAST",
                "items": [
                    {"food_name": "Paratha", "quantity": "2 pieces"},
                    {"food_name": "Tea", "quantity": "1 cup"},
                ],
            },
        )
        assert response.status_code in (201, 200, 409)

    async def test_create_menu_customer_forbidden(self, client: AsyncClient, customer_user: User):
        from tests.conftest import make_access_token
        token = make_access_token(customer_user)
        response = await client.post(
            "/api/v1/dining/menus",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "date": date.today().isoformat(),
                "meal_type": "LUNCH",
                "items": [{"food_name": "Rice"}],
            },
        )
        assert response.status_code == 403


class TestCustomerManagementEndpoints:
    async def test_list_customers_as_manager(self, client: AsyncClient, manager_user: User):
        from tests.conftest import make_access_token
        token = make_access_token(manager_user)
        response = await client.get(
            "/api/v1/customers",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

    async def test_list_customers_as_customer_forbidden(self, client: AsyncClient, customer_user: User):
        from tests.conftest import make_access_token
        token = make_access_token(customer_user)
        response = await client.get(
            "/api/v1/customers",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    async def test_add_customer_noncustomer_to_customer(
        self, client: AsyncClient, manager_user: User, noncustomer_user: User
    ):
        from tests.conftest import make_access_token
        token = make_access_token(manager_user)
        response = await client.post(
            f"/api/v1/customers/{noncustomer_user.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code in (200, 201, 409)


class TestTodayMealsEndpoints:
    async def test_today_status_for_customer(self, client: AsyncClient, customer_user: User):
        from tests.conftest import make_access_token
        token = make_access_token(customer_user)
        response = await client.get(
            "/api/v1/meals/today",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    async def test_today_status_non_customer_forbidden(self, client: AsyncClient, noncustomer_user: User):
        from tests.conftest import make_access_token
        token = make_access_token(noncustomer_user)
        response = await client.get(
            "/api/v1/meals/today",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
