from shipment_tracking_api.models.shipment_model import Shipment
from shipment_tracking_api.repositories.base_repository import BaseRepository


class ShipmentRepository(BaseRepository[Shipment]):
    model = Shipment

    