"""Pydantic schemas for authentication requests and responses."""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Schema for user registration with email and password."""

    email: EmailStr
    password: str = Field(..., min_length=6)
    first_name: str = Field(..., alias="firstName", max_length=255)
    last_name: str = Field(..., alias="lastName", max_length=255)

    model_config = {"populate_by_name": True}


class LoginRequest(BaseModel):
    """Schema for user login with email and password."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Schema for login response with JWT token and user information."""

    token: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
