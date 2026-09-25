from unittest.mock import AsyncMock, call

import pytest
from sqlalchemy.exc import IntegrityError

from shipment_tracking_api.errors_handling.shipment_errors import (
    ShipmentTrackingNumberAlreadyExists,
)
from shipment_tracking_api.infrastructure.cache.cache_keys import CacheKeys
from shipment_tracking_api.models.shipment_model import Status
from shipment_tracking_api.schemas.shipment import (
    ShipmentCreateSchema,
    ShipmentReadSchema,
)
from shipment_tracking_api.services.shipment_service import ShipmentService
from tests.factories import ShipmentFactory, UserFactory


@pytest.mark.asyncio
async def test_get_all_shipments_cache_miss():
    repo = AsyncMock()
    cache = AsyncMock()

    service = ShipmentService(
        shipment_repo=repo,
        cache=cache,
    )

    shipment = ShipmentFactory.build(id=123, user=UserFactory.build(id=222))
    expected = ShipmentReadSchema.model_validate(shipment)

    cache.get.return_value = None
    repo.get_all_shipments.return_value = [expected]

    result = await service.get_all_shipments(user_id=shipment.user.id)

    assert result == [expected]

    repo.get_all_shipments.assert_awaited_once_with(user_id=shipment.user.id)

    cache.get.assert_awaited_once_with(
        CacheKeys.user_shipments(shipment.user.id),
    )

    cache.set.assert_awaited_once_with(
        CacheKeys.user_shipments(shipment.user.id),
        [expected.model_dump(mode="json")],
    )


@pytest.mark.asyncio
async def test_get_all_shipments_with_cache():
    repo = AsyncMock()
    cache = AsyncMock()

    service = ShipmentService(
        shipment_repo=repo,
        cache=cache,
    )

    shipment = ShipmentFactory.build(
        id=1,
        user=UserFactory.build(id=123),
    )

    cached_shipments = [
        ShipmentReadSchema.model_validate(shipment).model_dump(mode="json")
    ]

    cache.get.return_value = cached_shipments

    result = await service.get_all_shipments(user_id=shipment.user.id)

    assert len(result) == 1
    assert result[0].id == shipment.id

    cache.get.assert_awaited_once_with(
        CacheKeys.user_shipments(shipment.user.id),
    )

    repo.get_all_shipments.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_shipment_by_id_cache_miss():
    repo = AsyncMock()
    cache = AsyncMock()

    service = ShipmentService(
        shipment_repo=repo,
        cache=cache,
    )

    shipment = ShipmentFactory.build(id=123, user=UserFactory.build(id=222))

    cache.get.return_value = None
    repo.get_shipment_by_id.return_value = shipment

    result = await service.get_shipment_by_id(
        shipment_id=shipment.id, user_id=shipment.user.id
    )

    expected = ShipmentReadSchema.model_validate(shipment)

    assert result == expected

    cache.get.assert_awaited_once_with(
        CacheKeys.shipment(shipment.id),
    )

    repo.get_shipment_by_id.assert_awaited_once_with(
        shipment_id=shipment.id, user_id=shipment.user.id
    )

    cache.set.assert_awaited_once_with(
        CacheKeys.shipment(shipment.id),
        expected.model_dump(mode="json"),
    )


@pytest.mark.asyncio
async def test_get_shipment_by_id_cache_hit():
    repo = AsyncMock()
    cache = AsyncMock()

    service = ShipmentService(
        shipment_repo=repo,
        cache=cache,
    )

    shipment = ShipmentFactory.build(
        id=123,
        user=UserFactory.build(id=222),
    )

    expected = ShipmentReadSchema.model_validate(shipment)
    cache.get.return_value = expected.model_dump(mode="json")

    result = await service.get_shipment_by_id(
        shipment_id=shipment.id,
        user_id=shipment.user.id,
    )

    assert result == expected

    cache.get.assert_awaited_once_with(
        CacheKeys.shipment(shipment.id),
    )

    repo.get_shipment_by_id.assert_not_awaited()

    cache.set.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_shipment():
    repo = AsyncMock()
    cache = AsyncMock()

    service = ShipmentService(
        shipment_repo=repo,
        cache=cache,
    )

    data = ShipmentCreateSchema(
        tracking_number=123456,
    )

    shipment = ShipmentFactory.build(
        id=1,
        user_id=123,
        status=Status.assembling,
        tracking_number=data.tracking_number,
    )

    repo.add.return_value = shipment

    result = await service.add_shipment(
        data=data,
        user_id=shipment.user_id,
    )

    expected = ShipmentReadSchema.model_validate(shipment)

    assert result == expected

    repo.add.assert_awaited_once()

    added_shipment = repo.add.await_args.args[0]

    assert added_shipment.user_id == shipment.user_id
    assert added_shipment.status == Status.assembling
    assert added_shipment.tracking_number == data.tracking_number

    cache.delete.assert_awaited_once_with(
        CacheKeys.user_shipments(shipment.user_id),
    )


@pytest.mark.asyncio
async def test_add_shipment_tracking_number_already_exists():
    repo = AsyncMock()
    cache = AsyncMock()

    service = ShipmentService(
        shipment_repo=repo,
        cache=cache,
    )

    data = ShipmentCreateSchema(
        tracking_number=123456,
    )

    repo.add.side_effect = IntegrityError(
        "duplicate tracking number",
        params=None,
        orig=ValueError("duplicate tracking number"),
    )

    with pytest.raises(ShipmentTrackingNumberAlreadyExists) as exc_info:
        await service.add_shipment(
            data=data,
            user_id=123,
        )

    assert exc_info.value.args[0] == data.tracking_number

    repo.add.assert_awaited_once()

    cache.delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_shipment_by_id():
    repo = AsyncMock()
    cache = AsyncMock()

    service = ShipmentService(
        shipment_repo=repo,
        cache=cache,
    )

    shipment = ShipmentFactory.build(
        id=123,
        user=UserFactory.build(id=222),
    )

    repo.get_shipment_by_id.return_value = shipment

    await service.delete_shipment_by_id(
        user_id=shipment.user.id,
        shipment_id=shipment.id,
    )

    repo.get_shipment_by_id.assert_awaited_once_with(
        shipment_id=shipment.id,
        user_id=shipment.user.id,
    )

    cache.delete.assert_has_awaits(
        [
            call(CacheKeys.user_shipments(shipment.user.id)),
            call(CacheKeys.shipment(shipment.id)),
        ]
    )

    repo.delete.assert_awaited_once_with(shipment.id)
