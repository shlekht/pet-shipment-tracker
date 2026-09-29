import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class ShipmentNotFoundError(Exception):
    def __init__(self, shipment_id: int):
        self.message = f"Shipment with id = {shipment_id} not found."
        self.shipment_id = shipment_id


class ShipmentTrackingNumberAlreadyExists(Exception):
    def __init__(self, tracking_number: int):
        self.message = f"Shipment with tracking_number = {tracking_number} already exists. It must be unique."
        self.tracking_number = tracking_number


async def handle_shipment_not_found_error(
    request: Request, exc: ShipmentNotFoundError
) -> JSONResponse:
    logger.info(  # ожидаемое поведение, поэтому info, а не warning/error
        "Shipment not found: shipment_id=%s",
        exc.shipment_id
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": exc.message},
    )


async def handle_shipment_tracking_number_already_exists_error(
    request: Request, exc: ShipmentNotFoundError
) -> JSONResponse:
    body = await request.json()
    logger.info(  # ожидаемое поведение, поэтому info, а не warning/error
        "Shipment adding failure, tracking number %s already exists",
        body.get("tracking_number"),
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"message": exc.message},
    )
