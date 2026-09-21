from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from shipment_tracking_api.infrastructure.cache.redis import RedisCacheBackend
from shipment_tracking_api.infrastructure.database.database import async_session_maker
from shipment_tracking_api.infrastructure.message_broker.rabbitmq import RabbitMQ
from shipment_tracking_api.repositories.shipment_repository import ShipmentRepository
from shipment_tracking_api.repositories.user_repository import UserRepository
from shipment_tracking_api.services.auth_service import AuthService
from shipment_tracking_api.services.shipment_service import ShipmentService


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
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


SessionDependency = Annotated[AsyncSession, Depends(get_session)]


async def get_user_repository(
    session: SessionDependency,
) -> UserRepository:
    return UserRepository(session)


UserRepositoryDependency = Annotated[UserRepository, Depends(get_user_repository)]


async def get_auth_service(
    repository: UserRepositoryDependency,
) -> AuthService:
    return AuthService(repository)


async def get_shipment_repository(
    session: SessionDependency,
) -> ShipmentRepository:
    return ShipmentRepository(session)


ShipmentRepositoryDependency = Annotated[
    ShipmentRepository, Depends(get_shipment_repository)
]


async def get_shipment_service(
    repository: ShipmentRepositoryDependency,
) -> ShipmentService:
    return ShipmentService(repository)
