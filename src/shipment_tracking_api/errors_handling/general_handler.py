from typing import cast

from fastapi import FastAPI
from starlette.types import ExceptionHandler

from shipment_tracking_api.errors_handling.auth_errors import (
    AuthenticationError,
    UserAlreadyExistsError,
    handle_authentication_error,
    handle_user_already_exists_error,
)


def register_errors_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        AuthenticationError, cast(ExceptionHandler, handle_authentication_error)
    )
    app.add_exception_handler(
        UserAlreadyExistsError, cast(ExceptionHandler, handle_user_already_exists_error)
    )
