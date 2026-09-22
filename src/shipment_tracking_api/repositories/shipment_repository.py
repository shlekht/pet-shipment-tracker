from sqlalchemy import select

from shipment_tracking_api.models.shipment_model import Shipment
from shipment_tracking_api.repositories.base_repository import BaseRepository


class ShipmentRepository(BaseRepository[Shipment]):
    model = Shipment

    async def get_all_shipments(self, user_id: int) -> list[Shipment]:
        query = select(Shipment).where(Shipment.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_shipment_by_id(
        self, shipment_id: int, user_id: int
    ) -> Shipment | None:
        query = select(Shipment).where(
            Shipment.id == shipment_id, Shipment.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()



