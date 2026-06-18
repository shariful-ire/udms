"""Integration tests for expense management endpoints."""
import pytest
from datetime import date
from httpx import AsyncClient
from app.models.user import User


pytestmark = pytest.mark.asyncio


class TestExpenseEndpoints:
    async def test_create_expense_as_manager(self, client: AsyncClient, manager_user: User):
        from tests.conftest import make_access_token
        token = make_access_token(manager_user)
        response = await client.post(
            "/api/v1/expenses",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Test Rice Purchase",
                "category": "FOOD_PURCHASE",
                "amount": 5000.00,
                "description": "Monthly rice purchase for testing",
                "expense_date": date.today().isoformat(),
            },
        )
        assert response.status_code in (200, 201)
        data = response.json()
        assert data["success"] is True

    async def test_create_expense_customer_forbidden(self, client: AsyncClient, customer_user: User):
        from tests.conftest import make_access_token
        token = make_access_token(customer_user)
        response = await client.post(
            "/api/v1/expenses",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Forbidden Expense",
                "category": "MISCELLANEOUS",
                "amount": 100.00,
                "expense_date": date.today().isoformat(),
            },
        )
        assert response.status_code == 403

    async def test_list_expenses_as_manager(self, client: AsyncClient, manager_user: User):
        from tests.conftest import make_access_token
        token = make_access_token(manager_user)
        response = await client.get(
            "/api/v1/expenses",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

    async def test_list_expenses_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/v1/expenses")
        assert response.status_code == 401

    async def test_expense_pagination(self, client: AsyncClient, manager_user: User):
        from tests.conftest import make_access_token
        token = make_access_token(manager_user)

        # Create multiple expenses
        for i in range(3):
            await client.post(
                "/api/v1/expenses",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "name": f"Pagination Test Expense {i}",
                    "category": "MISCELLANEOUS",
                    "amount": float(100 + i),
                    "expense_date": date.today().isoformat(),
                },
            )

        response = await client.get(
            "/api/v1/expenses?page=1&per_page=2",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "meta" in data
        assert data["meta"]["per_page"] == 2

    async def test_update_expense(self, client: AsyncClient, manager_user: User):
        from tests.conftest import make_access_token
        token = make_access_token(manager_user)

        # Create first
        create_resp = await client.post(
            "/api/v1/expenses",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Updatable Expense",
                "category": "UTILITIES",
                "amount": 1000.00,
                "expense_date": date.today().isoformat(),
            },
        )
        if create_resp.status_code not in (200, 201):
            pytest.skip("Expense creation failed — skipping update test")

        expense_id = create_resp.json()["data"]["id"]

        update_resp = await client.put(
            f"/api/v1/expenses/{expense_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Updated Expense Name", "amount": 1500.00},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["data"]["name"] == "Updated Expense Name"

    async def test_delete_expense(self, client: AsyncClient, manager_user: User):
        from tests.conftest import make_access_token
        token = make_access_token(manager_user)

        create_resp = await client.post(
            "/api/v1/expenses",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Deletable Expense",
                "category": "MISCELLANEOUS",
                "amount": 500.00,
                "expense_date": date.today().isoformat(),
            },
        )
        if create_resp.status_code not in (200, 201):
            pytest.skip("Expense creation failed — skipping delete test")

        expense_id = create_resp.json()["data"]["id"]
        delete_resp = await client.delete(
            f"/api/v1/expenses/{expense_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert delete_resp.status_code == 200


class TestReportEndpoints:
    async def test_daily_report_as_manager(self, client: AsyncClient, manager_user: User):
        from tests.conftest import make_access_token
        token = make_access_token(manager_user)
        today = date.today().isoformat()
        response = await client.get(
            f"/api/v1/reports/daily?date={today}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

    async def test_monthly_report_as_provost(self, client: AsyncClient, provost_user: User):
        from tests.conftest import make_access_token
        token = make_access_token(provost_user)
        response = await client.get(
            f"/api/v1/reports/monthly?year=2024&month=6",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

    async def test_reports_customer_forbidden(self, client: AsyncClient, customer_user: User):
        from tests.conftest import make_access_token
        token = make_access_token(customer_user)
        today = date.today().isoformat()
        response = await client.get(
            f"/api/v1/reports/daily?date={today}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
