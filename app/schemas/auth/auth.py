from __future__ import annotations

from pydantic import EmailStr

from app.schemas.base import AppSchema
from .user import UserResponse


class LoginRequest(AppSchema):
    email: EmailStr
    password: str


class RefreshTokenRequest(AppSchema):
    refresh_token: str


class TokenResponse(AppSchema):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class LoginResponse(AppSchema):
    user: UserResponse
    tokens: TokenResponse


class MessageResponse(AppSchema):
    message: str
