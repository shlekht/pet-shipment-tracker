from typing import Annotated

from fastapi import APIRouter, Depends, status

from shipment_tracking_api.dependencies import get_current_user, get_shipment_service
from shipment_tracking_api.infrastructure.tasks.tasks import (
    send_notification_about_status,
)
from shipment_tracking_api.models.user_model import User
from shipment_tracking_api.schemas.shipment import (
    ShipmentCreateSchema,
    ShipmentReadSchema,
    ShipmentStatusUpdateSchema,
)
from shipment_tracking_api.services.shipment_service import ShipmentService

router = APIRouter(prefix="/shipments", tags=["Shipments"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_shipments(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ShipmentService, Depends(get_shipment_service)],
) -> list[ShipmentReadSchema]:
    shipments = await service.get_all_shipments(user_id=current_user.id)
    return shipments


@router.get("/{shipment_id}", status_code=status.HTTP_200_OK)
async def get_shipment_by_id(
    shipment_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ShipmentService, Depends(get_shipment_service)],
) -> ShipmentReadSchema:
    return await service.get_shipment_by_id(
        shipment_id=shipment_id, user_id=current_user.id
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_shipment(
    data: ShipmentCreateSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ShipmentService, Depends(get_shipment_service)],
) -> ShipmentReadSchema:
    return await service.add_shipment(data=data, user_id=current_user.id)


@router.delete("/{shipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shipment_by_id(
    shipment_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ShipmentService, Depends(get_shipment_service)],
) -> None:
    await service.delete_shipment_by_id(
        user_id=current_user.id, shipment_id=shipment_id
    )


@router.patch("/{shipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_shipment_status(
    shipment_id: int,
    data: ShipmentStatusUpdateSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ShipmentService, Depends(get_shipment_service)],
) -> None:
    shipment_data = await service.update_shipment_status_by_id(shipment_id, data)
    send_notification_about_status.delay( # type: ignore
        shipment_data.model_dump(mode="json"), str(current_user.email)
    )
