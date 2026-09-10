import datetime
from typing import Annotated

from sqlalchemy import func, text
from sqlalchemy.orm import mapped_column

intpk = Annotated[int, mapped_column(primary_key=True)]

created_at = Annotated[
    datetime.datetime,
    mapped_column(server_default=text("TIMEZONE('utc', now())")),
]

updated_at = Annotated[
    datetime.datetime,
    mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=func.timezone("utc", func.now()),
    ),
]
