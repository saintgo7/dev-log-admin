"""
Test fixtures and configuration
"""
import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.db.session import Base, get_db
from app.main import app
from app.models.user import User
from app.models.team import Team, TeamMember
from app.core.security import hash_password, create_access_token


# Test database URL (use SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async_session = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with overridden database"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user"""
    user = User(
        id=str(uuid4()),
        email="test@example.com",
        name="Test User",
        hashed_password=hash_password("password123"),
        is_active=True,
        is_verified=True,
        role="member"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin user"""
    user = User(
        id=str(uuid4()),
        email="admin@example.com",
        name="Admin User",
        hashed_password=hash_password("adminpass123"),
        is_active=True,
        is_verified=True,
        role="admin"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_team(db_session: AsyncSession, test_user: User) -> Team:
    """Create a test team with test_user as owner"""
    team = Team(
        id=str(uuid4()),
        name="Test Team",
        slug="test-team",
        description="A test team"
    )
    db_session.add(team)
    await db_session.flush()

    membership = TeamMember(
        team_id=team.id,
        user_id=test_user.id,
        role="owner",
        is_active=True
    )
    db_session.add(membership)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authorization headers for test user"""
    token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(admin_user: User) -> dict:
    """Create authorization headers for admin user"""
    token = create_access_token(subject=admin_user.id)
    return {"Authorization": f"Bearer {token}"}
