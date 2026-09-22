import datetime

from pydantic import BaseModel, ConfigDict

from shipment_tracking_api.models.shipment_model import Status


class ShipmentCreateSchema(BaseModel):
    tracking_number: int


class ShipmentReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: Status
    tracking_number: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
