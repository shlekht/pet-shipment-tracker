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
)


class ShipmentService:
    def __init__(self, shipment_repo: ShipmentRepository, cache: RedisCacheBackend):
        self.shipment_repo = shipment_repo
        self.cache = cache

    async def get_all_shipments(self, user_id: int) -> list[ShipmentReadSchema]:
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
        shipments_for_cache = [shipment.model_dump(mode="json") for shipment in shipments_read]
        await self.cache.set(cache_key, shipments_for_cache)
        return shipments_read

    async def get_shipment_by_id(
        self, shipment_id: int, user_id: int
    ) -> ShipmentReadSchema:
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

        return shipment_read

    async def add_shipment(
        self, data: ShipmentCreateSchema, user_id: int
    ) -> ShipmentReadSchema:

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

        return ShipmentReadSchema.model_validate(shipment)

    async def delete_shipment_by_id(self, user_id: int, shipment_id: int):

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
