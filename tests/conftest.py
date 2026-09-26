import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import redis.asyncio as redis
from shipment_tracking_api.config import settings
from shipment_tracking_api.dependencies import get_redis, get_session
from shipment_tracking_api.infrastructure.cache.redis import RedisCacheBackend
from shipment_tracking_api.infrastructure.database.database import Base
from shipment_tracking_api.main import app as fastapi_app
from tests.factories import UserFactory

test_engine = create_async_engine(
    str(settings.TEST_DATABASE_URL),
    poolclass=NullPool,
)


@pytest_asyncio.fixture(scope="session")
async def setup_db():
    assert settings.TEST_DATABASE_URL != settings.DATABASE_URL
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_db):
    async with test_engine.connect() as conn:
        trans = await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        yield session
        await session.close()
        await trans.rollback()


@pytest_asyncio.fixture(scope="function")
async def redis_client():
    client = RedisCacheBackend.from_url(settings.TEST_REDIS_URL, cache_ttl_seconds=60)
    await client.ping()
    yield client
    await client.flushdb()
    await client.close()


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session, redis_client):
    async def override_get_db():
        yield db_session

    async def override_get_redis():
        return redis_client

    fastapi_app.dependency_overrides[get_session] = override_get_db
    fastapi_app.dependency_overrides[get_redis] = override_get_redis
    transport = ASGITransport(app=fastapi_app)
    try:
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as ac:
            yield ac
    finally:
        fastapi_app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def authenticated_async_client(async_client, user):
    response = await async_client.post(
        "/auth/login",
        json={
            "email": user.email,
            "password": "test123",
        },
    )
    assert response.status_code == 204
    assert async_client.cookies.get("shipment_token")
    return async_client


@pytest_asyncio.fixture(scope="function")
async def user(db_session):
    user = UserFactory.build(
        email="test@example.com",
    )
    db_session.add(user)
    await db_session.flush()
    return user
