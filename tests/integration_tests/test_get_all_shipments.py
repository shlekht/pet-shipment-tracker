import pytest

from tests.factories import ShipmentFactory, UserFactory


@pytest.mark.asyncio
async def test_get_all_shipments(
    authenticated_async_client,
    db_session,
    user,
):
    shipment_own_by_current_user_1 = ShipmentFactory.build(
        user=user,
        tracking_number=100001,
    )
    shipment_own_by_current_user_2 = ShipmentFactory.build(
        user=user,
        tracking_number=100002,
    )
    shipment_own_by_another_user = ShipmentFactory.build(
        user=UserFactory.build(email="another@example.com"),
        tracking_number=2222,
    )

    db_session.add_all(
        [
            shipment_own_by_current_user_1,
            shipment_own_by_current_user_2,
            shipment_own_by_another_user,
        ]
    )
    await db_session.flush()

    response = await authenticated_async_client.get("/shipments/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    tracking_numbers = {shipment["tracking_number"] for shipment in data}

    assert tracking_numbers == {
        100001,
        100002,
    }  

    assert 2222 not in tracking_numbers
