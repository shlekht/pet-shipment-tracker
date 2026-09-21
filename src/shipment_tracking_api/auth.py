import datetime

import bcrypt
from jose import jwt

from shipment_tracking_api.config import settings


def get_password_hash(password: str) -> str:
    # 1. Convert string password to bytes
    password_bytes = password.encode("utf-8")

    # 2. Generate a secure salt (defaults to 12 rounds)
    salt = bcrypt.gensalt()

    # 3. Hash the password and decode the resulting bytes back to a string for database storage
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password, hashed_password) -> bool:
    plain_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")

    # Check if they match
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, settings.JWT_ALG)
    return encoded_jwt
