from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped, mapped_column

from delivery_tracking_api.infrastructure.database.annotations import (
    created_at,
    intpk,
)
from delivery_tracking_api.infrastructure.database.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    username: Mapped[str] = mapped_column(nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at: Mapped[created_at] = mapped_column(nullable=False)
