from shipment_tracking_api.repositories.shipment_repository import ShipmentRepository


class ShipmentService:
    def __init__(self, shipment_repo: ShipmentRepository):
        self.shipment_repo = shipment_repo

    async def get_all_shipments(self):
        pass

    async def get_shipment_by_id(self, id):
        pass

    async def add_shipment(self):
        pass

    async def delete_shipment_by_id(self, id):
        pass
