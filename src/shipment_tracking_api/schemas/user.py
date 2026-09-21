import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    created_at: datetime.datetime

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str = Field(min_length=4, max_length=128)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4, max_length=128)


    