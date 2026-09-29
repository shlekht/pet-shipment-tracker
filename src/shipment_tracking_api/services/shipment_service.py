import logging

from sqlalchemy.exc import IntegrityError

from shipment_tracking_api.errors_handling.shipment_errors import (
    ShipmentNotFoundError,
    ShipmentTrackingNumberAlreadyExists,
)
from shipment_tracking_api.infrastructure.cache.cache_keys import CacheKeys
from shipment_tracking_api.infrastructure.cache.redis import RedisCacheBackend
from shipment_tracking_api.models.shipment_model import Shipment, Status
from shipment_tracking_api.repositories.shipment_repository import ShipmentRepository
from shipment_tracking_api.schemas.shipment import (
    ShipmentCreateSchema,
    ShipmentReadSchema,
    ShipmentStatusUpdateSchema,
)

logger = logging.getLogger(__name__)


class ShipmentService:
    def __init__(self, shipment_repo: ShipmentRepository, cache: RedisCacheBackend):
        self.shipment_repo = shipment_repo
        self.cache = cache

    async def get_all_shipments(self, user_id: int) -> list[ShipmentReadSchema]:
        logger.info(
            "User is getting all shipments",
            extra={
                "user_id": str(user_id),
            },
        )
        cache_key = CacheKeys.user_shipments(user_id)
        cached_shipments = await self.cache.get(cache_key)
        if cached_shipments is not None:
            return [
                ShipmentReadSchema.model_validate(shipment)
                for shipment in cached_shipments
            ]

        shipments = await self.shipment_repo.get_all_shipments(user_id=user_id)
        shipments_read = [
            ShipmentReadSchema.model_validate(shipment) for shipment in shipments
        ]
        shipments_for_cache = [
            shipment.model_dump(mode="json") for shipment in shipments_read
        ]
        await self.cache.set(cache_key, shipments_for_cache)
        logger.info(
            "User got all shipments",
            extra={
                "user_id": str(user_id),
            },
        )
        return shipments_read

    async def get_shipment_by_id(
        self, shipment_id: int, user_id: int
    ) -> ShipmentReadSchema:
        logger.info(
            "User is getting a shipment",
            extra={
                "user_id": str(user_id),
                "shipment_id": str(shipment_id),
            },
        )
        cache_key = CacheKeys.shipment(shipment_id)
        cached_shipment = await self.cache.get(cache_key)
        if cached_shipment is not None:
            return ShipmentReadSchema.model_validate(cached_shipment)

        shipment = await self.shipment_repo.get_shipment_by_id(
            shipment_id=shipment_id, user_id=user_id
        )
        if shipment is None:
            raise ShipmentNotFoundError(shipment_id)
        shipment_read = ShipmentReadSchema.model_validate(shipment)
        shipment_for_cache = shipment_read.model_dump(mode="json")
        await self.cache.set(cache_key, shipment_for_cache)
        logger.info(
            "User got a shipment",
            extra={
                "user_id": str(user_id),
                "shipment_id": str(shipment_id),
            },
        )
        return shipment_read

    async def add_shipment(
        self, data: ShipmentCreateSchema, user_id: int
    ) -> ShipmentReadSchema:
        logger.info(
            "User is adding a shipment",
            extra={
                "user_id": str(user_id),
                "tracking_number": str(data.tracking_number),
            },
        )
        shipment_to_add = Shipment(
            user_id=user_id,
            status=Status.assembling,
            tracking_number=data.tracking_number,
        )
        try:
            shipment = await self.shipment_repo.add(shipment_to_add)
        except IntegrityError:
            raise ShipmentTrackingNumberAlreadyExists(data.tracking_number)

        # Инвалидация кэша после успешной записи чтобы избежать race condition с get_all_shipments()
        cache_key = CacheKeys.user_shipments(user_id)
        await self.cache.delete(cache_key)
        logger.info(
            "User added a shipment",
            extra={
                "user_id": str(user_id),
                "shipment_id": str(shipment.id),
            },
        )
        return ShipmentReadSchema.model_validate(shipment)

    async def delete_shipment_by_id(self, user_id: int, shipment_id: int):
        logger.info(
            "User is deleting a shipment",
            extra={
                "user_id": str(user_id),
                "shipment_id": str(shipment_id),
            },
        )

        shipment = await self.shipment_repo.get_shipment_by_id(
            shipment_id=shipment_id, user_id=user_id
        )
        # None вернётся если такого shipment нет или если нет прав на удаление (user_id не владельца)

        if shipment is None:
            raise ShipmentNotFoundError(
                shipment_id
            )  # чтобы не раскрывать существует ли сущность вообще, в любом случае отправляем 404. Но это компромисс между UX и безопасностью

        # Инвалидация и всего списка сущностей, и самой сущности
        await self.cache.delete(CacheKeys.user_shipments(user_id))
        await self.cache.delete(CacheKeys.shipment(shipment_id))

        await self.shipment_repo.delete(shipment_id)
        logger.info(
            "User deleted a shipment",
            extra={
                "user_id": str(user_id),
                "shipment_id": str(shipment_id),
            },
        )

    # Тестовая имитация другого сервиса, поэтому без проверки прав и т.д.
    async def update_shipment_status_by_id(
        self, shipment_id: int, data: ShipmentStatusUpdateSchema
    ) -> ShipmentReadSchema:
        logger.info(
            "Updating a shipment",
            extra={
                "shipment_id": str(shipment_id),
            },
        )
        shipment = await self.shipment_repo.get_by_id(shipment_id)
        if shipment is None:
            raise ShipmentNotFoundError(shipment_id)
        shipment.status = data.status
        logger.info(
            "Updated a shipment",
            extra={
                "shipment_id": str(shipment_id),
            },
        )
        return ShipmentReadSchema.model_validate(shipment)
