from fastapi import Request, status
from fastapi.responses import JSONResponse


class ShipmentNotFoundError(Exception):
    def __init__(self, shipment_id: int):
        self.message = f"Shipment with id = {shipment_id} not found."


class ShipmentTrackingNumberAlreadyExists(Exception):
    def __init__(self, tracking_number: int):
        self.message = f"Shipment with tracking_number = {tracking_number} already exists. It must be unique."


async def handle_shipment_not_found_error(
    request: Request, exc: ShipmentNotFoundError
) -> JSONResponse:
    # logging here later
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": exc.message},
    )


async def handle_shipment_tracking_number_already_exists_error(
    request: Request, exc: ShipmentNotFoundError
) -> JSONResponse:
    # logging here later
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"message": exc.message},
    )
