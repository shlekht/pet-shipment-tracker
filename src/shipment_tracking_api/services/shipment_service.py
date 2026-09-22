from sqlalchemy.exc import IntegrityError

from shipment_tracking_api.errors_handling.shipment_errors import (
    ShipmentNotFoundError,
    ShipmentTrackingNumberAlreadyExists,
)
from shipment_tracking_api.models.shipment_model import Shipment, Status
from shipment_tracking_api.repositories.shipment_repository import ShipmentRepository
from shipment_tracking_api.schemas.shipment import (
    ShipmentCreateSchema,
    ShipmentReadSchema,
)


class ShipmentService:
    def __init__(self, shipment_repo: ShipmentRepository):
        self.shipment_repo = shipment_repo

    async def get_all_shipments(self, user_id: int) -> list[ShipmentReadSchema]:
        shipments = await self.shipment_repo.get_all_shipments(user_id=user_id)
        return [ShipmentReadSchema.model_validate(s) for s in shipments]

    async def get_shipment_by_id(
        self, shipment_id: int, user_id: int
    ) -> ShipmentReadSchema:
        shipment = await self.shipment_repo.get_shipment_by_id(
            shipment_id=shipment_id, user_id=user_id
        )
        if shipment is None:
            raise ShipmentNotFoundError(shipment_id)
        return ShipmentReadSchema.model_validate(shipment)

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

        await self.shipment_repo.delete(shipment_id)
