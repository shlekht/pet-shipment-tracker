import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    created_at: datetime.datetime

class UserRegisterSchema(BaseModel):
    email: EmailStr
    username: str
    password: str = Field(min_length=4, max_length=128)

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4, max_length=128)


    