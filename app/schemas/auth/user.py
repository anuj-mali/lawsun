from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import EmailStr, Field, field_validator, ValidationInfo

from app.schemas.base import AppSchema
from app.models.user import UserRole


# User
class UserCreate(AppSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    first_name: str = Field(min_length=1, max_length=255)
    last_name: str = Field(min_length=1, max_length=255)
    middle_name: str | None = Field(min_length=1, max_length=255, default=None)
    role: UserRole = Field(default=UserRole.USER)


class UserUpdate(AppSchema):
    first_name: str | None = Field(min_length=1, max_length=255, default=None)
    last_name: str | None = Field(min_length=1, max_length=255, default=None)
    middle_name: str | None = Field(min_length=1, max_length=255, default=None)


class UserUpdateRole(AppSchema):
    role: UserRole


class UserResponse(AppSchema):
    id: uuid.UUID
    email: EmailStr
    first_name: str
    middle_name: str | None
    last_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


class UserListResponse(AppSchema):
    items: list[UserResponse]
    next_cursor: uuid.UUID | None


# Password
class PasswordChange(AppSchema):
    current_password: str = Field(min_length=8, max_length=64)
    new_password: str = Field(min_length=8, max_length=64)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, new: str, info: ValidationInfo) -> str:
        if new == info.data["current_password"]:
            raise ValueError("New password cannot be the same as the current password")
        return new


class PasswordResetRequest(AppSchema):
    email: EmailStr


class PasswordResetConfirm(AppSchema):
    token: str
    new_password: str = Field(min_length=8, max_length=64)
