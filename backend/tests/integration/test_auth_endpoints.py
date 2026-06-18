"""Integration tests for authentication endpoints."""
import pytest
import pytest_asyncio
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestRegistrationEndpoint:
    async def test_register_valid_user(self, client: AsyncClient):
        """A valid registration should return 201 with success=true."""
        response = await client.post("/api/v1/auth/register", json={
            "student_id": "CSE-INTG-001",
            "username": "intg_user1",
            "full_name": "Integration User One",
            "email": "intg1@university.edu",
            "password": "ValidPass@1234",
            "department": "CSE",
            "batch": "2024",
            "hall_name": "Shaheed Hall",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "intg_user1" in data["message"].lower() or "user" in data["message"].lower()

    async def test_register_duplicate_username_rejected(self, client: AsyncClient):
        """Duplicate username should return 409."""
        payload = {
            "student_id": "CSE-INTG-002",
            "username": "dup_user",
            "full_name": "Dup User",
            "email": "dup@university.edu",
            "password": "ValidPass@1234",
            "department": "CSE",
            "batch": "2024",
            "hall_name": "Shaheed Hall",
        }
        # First registration
        await client.post("/api/v1/auth/register", json=payload)

        # Duplicate
        payload["student_id"] = "CSE-INTG-099"
        payload["email"] = "dup2@university.edu"
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 409

    async def test_register_weak_password_rejected(self, client: AsyncClient):
        """Weak password should return 422."""
        response = await client.post("/api/v1/auth/register", json={
            "student_id": "CSE-INTG-003",
            "username": "weak_user",
            "full_name": "Weak User",
            "email": "weak@university.edu",
            "password": "weak",
            "department": "CSE",
            "batch": "2024",
            "hall_name": "Shaheed Hall",
        })
        assert response.status_code == 422

    async def test_register_invalid_email_rejected(self, client: AsyncClient):
        """Invalid email format should return 422."""
        response = await client.post("/api/v1/auth/register", json={
            "student_id": "CSE-INTG-004",
            "username": "bademail_user",
            "full_name": "Bad Email",
            "email": "not-an-email",
            "password": "ValidPass@1234",
            "department": "CSE",
            "batch": "2024",
            "hall_name": "Shaheed Hall",
        })
        assert response.status_code == 422


class TestLoginEndpoint:
    async def test_inactive_account_cannot_login(self, client: AsyncClient):
        """An unverified (INACTIVE) account should return 403."""
        # Register without verifying
        await client.post("/api/v1/auth/register", json={
            "student_id": "CSE-INTG-010",
            "username": "inactive_intg",
            "full_name": "Inactive User",
            "email": "inactive_intg@university.edu",
            "password": "ValidPass@1234",
            "department": "CSE",
            "batch": "2024",
            "hall_name": "Shaheed Hall",
        })
        # Try to login without verifying
        response = await client.post("/api/v1/auth/login", json={
            "identifier": "inactive_intg",
            "password": "ValidPass@1234",
        })
        assert response.status_code == 403

    async def test_nonexistent_user_returns_401(self, client: AsyncClient):
        """Login with unknown identifier should return 401."""
        response = await client.post("/api/v1/auth/login", json={
            "identifier": "nobody_user",
            "password": "SomePass@1234",
        })
        assert response.status_code == 401

    async def test_wrong_password_returns_401(self, client: AsyncClient):
        """Correct username but wrong password should return 401."""
        response = await client.post("/api/v1/auth/login", json={
            "identifier": "student_customer",
            "password": "WrongPass@999",
        })
        assert response.status_code == 401


class TestMeEndpoint:
    async def test_me_requires_auth(self, client: AsyncClient):
        """GET /me without token should return 401."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_me_with_valid_token(self, client: AsyncClient, customer_user):
        """GET /me with valid token should return user profile."""
        from tests.conftest import make_access_token
        token = make_access_token(customer_user)
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == customer_user.username
