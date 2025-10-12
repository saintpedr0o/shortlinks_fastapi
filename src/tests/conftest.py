import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from src.api.dependencies import get_db
from src.db import get_engine, get_session_factory
from sqlalchemy import text
from src.main import app


@pytest.fixture
async def engine():
    engine = get_engine()
    yield engine
    await engine.dispose()


@pytest.fixture
async def async_session(engine: AsyncEngine):
    SessionLocal = get_session_factory(engine)
    async with SessionLocal() as session:
        yield session


@pytest.fixture(autouse=True)
async def clean_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
        )
        tables = [row[0] for row in result.fetchall()]
        for table in tables:
            await conn.execute(
                text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE')
            )
    yield


@pytest.fixture
async def client(async_session: AsyncSession):
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.pop(get_db, None)
