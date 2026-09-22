from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from shipment_tracking_api.dependencies import get_shipment_service
from shipment_tracking_api.schemas.shipment import ShipmentReadSchema
from shipment_tracking_api.services.shipment_service import ShipmentService

router = APIRouter(prefix="/shipments", tags=["Shipments"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_shipments(
    current_user: ...,
    service: Annotated[ShipmentService, Depends(get_shipment_service)],
) -> list[ShipmentReadSchema]: ...


@router.get("/{id}", status_code=status.HTTP_200_CREATED)
async def get_shipment_by_id(
    id: int,
    current_user: ...,
    service: Annotated[ShipmentService, Depends(get_shipment_service)],
) -> ShipmentReadSchema: ...


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_shipment(
    current_user: ...,
    service: Annotated[ShipmentService, Depends(get_shipment_service)],
) -> ShipmentReadSchema: ...


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shipment_by_id(
    current_user: ...,
    service: Annotated[ShipmentService, Depends(get_shipment_service)],
) -> None: ...
