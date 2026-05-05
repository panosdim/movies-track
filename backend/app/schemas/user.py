from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: str | None = None
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: str | None = None
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)


class User(UserBase):
    id: int

    model_config = {"from_attributes": True}
