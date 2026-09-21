import enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from shipment_tracking_api.infrastructure.database.annotations import (
    CreatedAt,
    UpdatedAt,
    intpk,
)
from shipment_tracking_api.infrastructure.database.database import Base


class Status(enum.Enum):
    unknown = "unknown"
    assembling = "assembling"
    shipping = "shipping"
    delivered = "delivered"


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[Status] = mapped_column(nullable=False)
    tracking_number: Mapped[int] = mapped_column(unique=True, nullable=False)
    created_at: Mapped[CreatedAt]
    updated_at_at: Mapped[UpdatedAt]
