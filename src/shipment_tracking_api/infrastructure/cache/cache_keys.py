class CacheKeys:
    _NAMESPACE = "shipment_app"

    @staticmethod
    def user_shipments(user_id: int) -> str:
        return f"{CacheKeys._NAMESPACE}:user:{user_id}:shipments"

    @staticmethod
    def shipment(shipment_id: int) -> str:
        return f"{CacheKeys._NAMESPACE}:shipment:{shipment_id}"
