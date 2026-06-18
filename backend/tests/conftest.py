"""
Pytest configuration — shared fixtures for unit and integration tests.
"""
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

# Use SQLite in-memory for testing (no MySQL required)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create a new event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create an in-memory SQLite engine with all tables."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )

    from app.db.base import Base
    from app.models import *  # noqa: F401, F403

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional test DB session that rolls back after each test."""
    TestSessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with TestSessionLocal() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest_asyncio.fixture
async def app():
    """Create the FastAPI app with test DB override."""
    from app.main import create_app
    from app.api.v1.deps import get_db
    from app.db.session import AsyncSessionLocal

    application = create_app()

    # Override DB dependency with test DB
    async def override_get_db():
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
        engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
        TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with TestSession() as session:
            yield session

    application.dependency_overrides[get_db] = override_get_db
    return application


@pytest_asyncio.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for integration tests."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def provost_user(db: AsyncSession):
    """Create and return a Provost user for tests."""
    from app.models.user import User
    from app.core.security import hash_password

    user = User(
        student_id="PROVOST-TEST-001",
        username="test_provost",
        full_name="Test Provost",
        email="provost@test.edu",
        password_hash=hash_password("Admin@1234!"),
        role="PROVOST",
        department="Administration",
        batch="N/A",
        hall_name="Admin Block",
        status="ACTIVE",
        email_verified=True,
    )
    db.add(user)
    await db.flush()
    return user


@pytest_asyncio.fixture
async def manager_user(db: AsyncSession):
    """Create and return a Dining Manager user for tests."""
    from app.models.user import User
    from app.core.security import hash_password

    user = User(
        student_id="MGR-TEST-001",
        username="test_manager",
        full_name="Test Manager",
        email="manager@test.edu",
        password_hash=hash_password("Manager@1234!"),
        role="DINING_MANAGER",
        department="Dining",
        batch="N/A",
        hall_name="Dining Hall",
        status="ACTIVE",
        email_verified=True,
    )
    db.add(user)
    await db.flush()
    return user


@pytest_asyncio.fixture
async def customer_user(db: AsyncSession):
    """Create and return a Customer user for tests."""
    from app.models.user import User
    from app.core.security import hash_password

    user = User(
        student_id="CSE-TEST-001",
        username="test_customer",
        full_name="Test Customer",
        email="customer@test.edu",
        password_hash=hash_password("Student@1234!"),
        role="CUSTOMER",
        department="CSE",
        batch="2021",
        hall_name="Shaheed Hall",
        status="ACTIVE",
        email_verified=True,
    )
    db.add(user)
    await db.flush()
    return user


@pytest_asyncio.fixture
async def noncustomer_user(db: AsyncSession):
    """Create and return a Non-Customer user for tests."""
    from app.models.user import User
    from app.core.security import hash_password

    user = User(
        student_id="EEE-TEST-001",
        username="test_noncustomer",
        full_name="Test Non-Customer",
        email="noncustomer@test.edu",
        password_hash=hash_password("Student@1234!"),
        role="NON_CUSTOMER",
        department="EEE",
        batch="2022",
        hall_name="Rokeya Hall",
        status="ACTIVE",
        email_verified=True,
    )
    db.add(user)
    await db.flush()
    return user


def make_access_token(user) -> str:
    """Generate a valid access token for a test user."""
    from app.core.security import create_access_token
    return create_access_token(
        user_id=str(user.id),
        username=user.username,
        role=user.role,
        email=user.email,
    )
