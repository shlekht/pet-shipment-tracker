import datetime

from pydantic import BaseModel

from shipment_tracking_api.models.shipment_model import Status


class ShipmentCreateSchema(BaseModel):
    user_id: int
    tracking_number: int

class ShipmentReadSchema(BaseModel):
    id: int
    status: Status
    tracking_number: int
    created_at: datetime.datetime
    updated_at: datetime.datetime