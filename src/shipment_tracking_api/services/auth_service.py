from shipment_tracking_api.auth import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from shipment_tracking_api.errors_handling.auth_errors import (
    AuthenticationError,
    UserAlreadyExistsError,
)
from shipment_tracking_api.models.user_model import User
from shipment_tracking_api.repositories.user_repository import UserRepository
from shipment_tracking_api.schemas.user import UserRegisterSchema


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise AuthenticationError()
        if not verify_password(password, user.hashed_password):
            raise AuthenticationError()
        return user

    async def login(self, email: str, password: str) -> str:
        user = await self.authenticate(email, password)
        return create_access_token({"sub": str(user.id)})

    async def register(self, data: UserRegisterSchema) -> User:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise UserAlreadyExistsError()

        user = User(
            email=data.email,
            username=data.username,
            hashed_password=get_password_hash(data.password),
        )
        return await self.user_repo.add(user)
