import pytest
from sqlalchemy import select

from shipment_tracking_api.models.shipment_model import Shipment, Status


@pytest.mark.asyncio
async def test_add_shipment_creates_shipment(
    authenticated_async_client,
    db_session,
    user,
):

    payload = {
        "tracking_number": 123456,
    }

    response = await authenticated_async_client.post(
        "/shipments/",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["tracking_number"] == 123456
    assert data["status"] == Status.assembling.value

    result = await db_session.execute(
        select(Shipment).where(Shipment.tracking_number == 123456)
    )
    shipment = result.scalar_one()
    assert shipment.user_id == user.id
    assert shipment.tracking_number == 123456
    assert shipment.status == Status.assembling
