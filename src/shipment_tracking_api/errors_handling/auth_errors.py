from fastapi import Request, status
from fastapi.responses import JSONResponse


class AuthenticationError(Exception):
    def __init__(self, message: str = "Invalid email or password"):
        self.message = message


class UserAlreadyExistsError(Exception):
    def __init__(self, message: str = "User with this email already exists"):
        self.message = message



async def handle_authentication_error(
    request: Request, exc: AuthenticationError
) -> JSONResponse:
    # logging here later
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"message": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def handle_user_already_exists_error(
    request: Request, exc: UserAlreadyExistsError
) -> JSONResponse:
    # logging here later
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": exc.message},
    )
