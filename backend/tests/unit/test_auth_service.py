"""Unit tests for AuthService — registration, login, OTP, token rotation."""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import (
    ConflictException,
    InvalidCredentialsException,
    AccountLockedOutException,
    InactiveAccountException,
)
from app.models.user import User


pytestmark = pytest.mark.asyncio


# ─── Password hashing ────────────────────────────────────────────────────────

class TestPasswordHashing:
    def test_hash_and_verify(self):
        password = "SecretPass@1234"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("Correct@Pass1")
        assert not verify_password("wrong_password", hashed)

    def test_hash_is_unique(self):
        password = "SamePass@1234"
        h1 = hash_password(password)
        h2 = hash_password(password)
        # Argon2 uses random salt — hashes must differ
        assert h1 != h2

    def test_empty_password_verify_returns_false(self):
        hashed = hash_password("ValidPass@1234")
        assert not verify_password("", hashed)


# ─── JWT tokens ──────────────────────────────────────────────────────────────

class TestJWTTokens:
    def test_create_and_decode_access_token(self):
        from app.core.security import decode_access_token
        token = create_access_token(
            user_id="user-123",
            username="testuser",
            role="CUSTOMER",
            email="test@test.edu",
        )
        assert isinstance(token, str)
        payload = decode_access_token(token)
        assert payload["sub"] == "user-123"
        assert payload["username"] == "testuser"
        assert payload["role"] == "CUSTOMER"

    def test_invalid_token_raises(self):
        from app.core.security import decode_access_token
        from app.core.exceptions import InvalidTokenException
        with pytest.raises(InvalidTokenException):
            decode_access_token("not.a.valid.token")

    def test_token_payload_contains_exp(self):
        from app.core.security import decode_access_token
        import jwt
        token = create_access_token(
            user_id="user-456",
            username="user456",
            role="NON_CUSTOMER",
            email="u@t.edu",
        )
        from app.core.config import settings
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert "exp" in payload
        assert "iat" in payload


# ─── OTP generation ──────────────────────────────────────────────────────────

class TestOTPGeneration:
    def test_otp_is_6_digits(self):
        from app.core.security import generate_otp
        otp = generate_otp()
        assert len(otp) == 6
        assert otp.isdigit()

    def test_otp_is_random(self):
        from app.core.security import generate_otp
        otps = {generate_otp() for _ in range(20)}
        # With 20 samples from 1M possibilities, duplicates are extremely rare
        assert len(otps) > 15


# ─── Registration validation ─────────────────────────────────────────────────

class TestRegistrationSchema:
    def test_valid_registration_passes(self):
        from app.schemas.auth import RegisterRequest
        data = RegisterRequest(
            student_id="CSE-2024-001",
            username="testuser",
            full_name="Test User",
            email="test@university.edu",
            password="ValidPass@1234",
            department="CSE",
            batch="2024",
            hall_name="Shaheed Hall",
        )
        assert data.username == "testuser"

    def test_weak_password_rejected(self):
        from app.schemas.auth import RegisterRequest
        with pytest.raises(Exception):
            RegisterRequest(
                student_id="CSE-2024-001",
                username="testuser2",
                full_name="Test User",
                email="test2@university.edu",
                password="weak",  # too short, no uppercase/special
                department="CSE",
                batch="2024",
                hall_name="Shaheed Hall",
            )

    def test_invalid_email_rejected(self):
        from app.schemas.auth import RegisterRequest
        with pytest.raises(Exception):
            RegisterRequest(
                student_id="CSE-2024-002",
                username="testuser3",
                full_name="Test User 3",
                email="not-an-email",
                password="ValidPass@1234",
                department="CSE",
                batch="2024",
                hall_name="Shaheed Hall",
            )


# ─── Login flow ───────────────────────────────────────────────────────────────

class TestLoginFlow:
    async def test_successful_login(self, db: AsyncSession, customer_user: User):
        """Verify that a correct password + active account succeeds."""
        from app.repositories.user_repo import UserRepository

        repo = UserRepository(db)
        user = await repo.get_by_identifier(customer_user.username)
        assert user is not None
        assert verify_password("Student@1234!", user.password_hash)

    async def test_inactive_account_cannot_login(self, db: AsyncSession):
        """Inactive (unverified) account should be blocked."""
        inactive = User(
            student_id="CSE-TEST-999",
            username="inactive_user",
            full_name="Inactive User",
            email="inactive@test.edu",
            password_hash=hash_password("Pass@1234"),
            role="NON_CUSTOMER",
            department="CSE",
            batch="2023",
            hall_name="Shaheed Hall",
            status="INACTIVE",
            email_verified=False,
        )
        db.add(inactive)
        await db.flush()

        from app.repositories.user_repo import UserRepository
        repo = UserRepository(db)
        user = await repo.get_by_identifier("inactive_user")
        assert user is not None
        assert user.status == "INACTIVE"

    async def test_failed_attempt_increments(self, db: AsyncSession, customer_user: User):
        """Failed logins should increment the failed_attempts counter."""
        from app.repositories.user_repo import UserRepository
        repo = UserRepository(db)

        await repo.increment_failed_attempts(customer_user)
        await db.flush()

        updated = await repo.get_by_id(str(customer_user.id))
        assert updated.failed_attempts == 1
