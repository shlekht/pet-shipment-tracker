import datetime
from typing import Annotated

from sqlalchemy import func, text
from sqlalchemy.orm import mapped_column

intpk = Annotated[int, mapped_column(primary_key=True)]

CreatedAt = Annotated[
    datetime.datetime,
    mapped_column(server_default=text("TIMEZONE('utc', now())"), nullable=False),
]

UpdatedAt = Annotated[
    datetime.datetime,
    mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=func.timezone("utc", func.now()),
        nullable=False
    ),
]
