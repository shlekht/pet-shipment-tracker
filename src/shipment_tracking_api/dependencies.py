from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from shipment_tracking_api.infrastructure.cache.redis import RedisCacheBackend
from shipment_tracking_api.infrastructure.database.database import async_session_maker
from shipment_tracking_api.infrastructure.message_broker.rabbitmq import RabbitMQ


async def get_redis(request: Request) -> RedisCacheBackend:
    """It takes our lifespan-initialized redis client from app.state"""
    redis_backend = getattr(request.app.state, "redis", None)
    if redis_backend is None:
        raise RuntimeError("Redis client is not initialized.")
    return redis_backend


async def get_rabbit(request: Request) -> RabbitMQ:
    """It takes our lifespan-initialized rabbit client from app.state"""
    rabbit_backend = getattr(request.app.state, "rabbit", None)
    if rabbit_backend is None:
        raise RuntimeError("Rabbit client is not initialized.")
    return rabbit_backend


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session