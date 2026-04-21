from __future__ import annotations

import jwt
import uuid
import secrets
from datetime import datetime, timedelta, UTC

from passlib.context import CryptContext

from app.core.config import config

from app.models.user import User

from app.schemas.auth import LoginResponse, UserResponse, TokenResponse

from app.core.exceptions import (
    AccountDisabledError,
    UserNotFoundError,
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
)

from app.repositories import UserRepository, TokenRepository


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, user_repo: UserRepository, token_repo: TokenRepository) -> None:
        self.user_repo = user_repo
        self.token_repo = token_repo

    # Password hashing and verification
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    # Token creation and verification
    def create_access_token(self, user_id: uuid.UUID) -> str:
        expires = datetime.now(UTC) + timedelta(
            minutes=config.auth.access_token_expire_minutes
        )

        return jwt.encode(
            {
                "sub": str(user_id),
                "exp": expires,
                "type": "access",
            },
            config.auth.secret_key,
            algorithm=config.auth.algorithm,
        )

    def decode_access_token(self, token: str) -> uuid.UUID:
        try:
            payload = jwt.decode(
                token,
                config.auth.secret_key,
                algorithms=[config.auth.algorithm],
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.InvalidTokenError:
            raise InvalidTokenError()

        if payload["type"] != "access":
            raise InvalidTokenError("Invalid token type")

        return uuid.UUID(payload["sub"])

    async def login(self, email: str, password: str) -> LoginResponse:
        user = await self.user_repo.get_by_email(email)

        if not user or not self.verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise AccountDisabledError()

        tokens = await self._issue_tokens(user.id)

        return LoginResponse(
            user=UserResponse.model_validate(user),
            tokens=tokens,
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        user_id = await self.token_repo.get_user_id_for_refresh_token(refresh_token)

        if not user_id:
            raise InvalidTokenError("Invalid or expired refresh token")

        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise UserNotFoundError()

        if not user.is_active:
            raise AccountDisabledError()

        await self.token_repo.revoke_refresh_token(refresh_token)

        return await self._issue_tokens(user.id)

    async def logout(self, refresh_token: str) -> None:
        await self.token_repo.revoke_refresh_token(refresh_token)

    async def _issue_tokens(self, user_id: uuid.UUID) -> TokenResponse:
        access_token = self.create_access_token(user_id)
        refresh_token = secrets.token_urlsafe(32)

        await self.token_repo.store_refresh_token(
            user_id=user_id,
            token=refresh_token,
            ttl_seconds=config.auth.refresh_token_expire_days * 24 * 60 * 60,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    # Password reset
    async def request_password_reset(self, email: str) -> str:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise UserNotFoundError()

        token = secrets.token_urlsafe(32)

        await self.token_repo.store_reset_token(
            user_id=user.id,
            token=token,
            ttl_seconds=3600,
        )

        return token

    async def confirm_password_reset(self, token: str, new_password: str) -> None:
        user_id = await self.token_repo.get_user_id_for_reset_token(token)

        if not user_id:
            raise InvalidTokenError("Invalid or expired reset token")

        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise UserNotFoundError()

        await self.user_repo.update(
            user, hashed_password=self.hash_password(new_password)
        )

        await self.token_repo.revoke_reset_token(token)

        await self.token_repo.revoke_all_refresh_tokens(user_id)

    async def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> None:
        if not self.verify_password(current_password, user.hashed_password):
            raise InvalidCredentialsError("Current password is incorrect")

        await self.user_repo.update(
            user, hashed_password=self.hash_password(new_password)
        )

        await self.token_repo.revoke_all_refresh_tokens(user.id)
