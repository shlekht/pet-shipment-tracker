from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from shipment_tracking_api.dependencies import get_auth_service
from shipment_tracking_api.schemas.user import (
    UserLoginSchema,
    UserReadSchema,
    UserRegisterSchema,
)
from shipment_tracking_api.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    data: UserRegisterSchema,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserReadSchema:
    user = await service.register(data)

    # FastAPI в рантайме преобразует тип с ORM объекта User на UserReadSchema, из-за этого типизатор выдаёт предупреждение.
    # Чтобы всё было аккуратно можно делать вот так:
    return UserReadSchema.model_validate(user)


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
async def login(
    data: UserLoginSchema,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    token = await service.login(data.email, data.password)
    response.set_cookie("shipment_token", token, httponly=True)
    # В теории здесь можно возвращать GET/me если клиенту надо


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    response.delete_cookie("shipment_token")
