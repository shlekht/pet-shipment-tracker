import factory
from factory import fuzzy

from shipment_tracking_api.auth import get_password_hash
from shipment_tracking_api.models.shipment_model import Shipment, Status
from shipment_tracking_api.models.user_model import User

_TEST_PASSWORD_HASH = get_password_hash("test123")


class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Faker("email")
    username = factory.Faker("user_name")
    hashed_password = _TEST_PASSWORD_HASH


class ShipmentFactory(factory.Factory):
    class Meta:
        model = Shipment

    user = factory.SubFactory(UserFactory)
    status = fuzzy.FuzzyChoice(Status)
    tracking_number = factory.Sequence(lambda n: 100000 + n)
