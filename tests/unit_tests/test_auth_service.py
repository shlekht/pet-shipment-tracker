from unittest.mock import AsyncMock, patch

import pytest

from shipment_tracking_api.errors_handling.auth_errors import AuthenticationError
from shipment_tracking_api.services.auth_service import AuthService
from tests.factories import UserFactory


@pytest.mark.asyncio
async def test_authenticate_success():

    repo = AsyncMock()
    service = AuthService(user_repo=repo)

    user = UserFactory.build()
    repo.get_by_email.return_value = user

    result = await service.authenticate(user.email, "test123")

    assert result == user
    repo.get_by_email.assert_awaited_once_with(user.email)


@pytest.mark.asyncio
async def test_authenticate_user_not_found():
    repo = AsyncMock()
    service = AuthService(user_repo=repo)

    user = UserFactory.build()
    repo.get_by_email.return_value = None

    with pytest.raises(AuthenticationError):
        await service.authenticate(
            user.email,
            "test123",
        )

    repo.get_by_email.assert_awaited_once_with(user.email)


@pytest.mark.asyncio
async def test_authenticate_wrong_password():
    repo = AsyncMock()
    service = AuthService(user_repo=repo)

    user = UserFactory.build()
    repo.get_by_email.return_value = user

    with pytest.raises(AuthenticationError):
        await service.authenticate(
            user.email,
            "wrong-password",
        )

    repo.get_by_email.assert_awaited_once_with(user.email)


@pytest.mark.asyncio
async def test_login_success():
    repo = AsyncMock()
    service = AuthService(user_repo=repo)

    user = UserFactory.build()

    with (
        patch.object(  # patch.object позволяет заменить результат мок-объектом.
            service,
            "authenticate",
            new=AsyncMock(
                return_value=user
            ),  # В данном случае мы меняем service.authenticate на AsyncMock
        ) as authenticate_mock,
        patch(
            "shipment_tracking_api.services.auth_service.create_access_token",
            return_value="access-token",  # а здесь меняем create_access_token из auth_service
        ) as create_token_mock,
    ):
        result = await service.login(
            user.email,
            "test123",
        )
    # patch.object временно заменяет объект у конкретного экземпляра. меняет service.authenticate
    # patch временно заменяет метод в модуле. меняет create_access_token в сервисе.

    assert result == "access-token"

    authenticate_mock.assert_awaited_once_with(
        user.email,
        "test123",
    )

    create_token_mock.assert_called_once_with({"sub": str(user.id)})
