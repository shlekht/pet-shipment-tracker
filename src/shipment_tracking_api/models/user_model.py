from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from shipment_tracking_api.infrastructure.database.annotations import (
    CreatedAt,
    intpk,
)
from shipment_tracking_api.infrastructure.database.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    username: Mapped[str] = mapped_column(nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[CreatedAt]
