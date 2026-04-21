from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.exceptions import AccountDisabledError, PermissionError, UserNotFoundError
from app.db.session import get_db
from app.db.redis import get_redis

from app.models.user import User, UserRole

from app.services.auth import AuthService
from app.repositories import UserRepository, TokenRepository

bearer_scheme = HTTPBearer()


def get_user_repo(db: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)


def get_token_repo(redis: Annotated[Redis, Depends(get_redis)]) -> TokenRepository:
    return TokenRepository(redis)


def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    token_repo: Annotated[TokenRepository, Depends(get_token_repo)],
) -> AuthService:
    return AuthService(user_repo=user_repo, token_repo=token_repo)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> User:
    user_id = auth_service.decode_access_token(credentials.credentials)

    user = await user_repo.get_by_id(user_id)

    if not user:
        raise UserNotFoundError()

    if not user.is_active:
        raise AccountDisabledError()

    return user


async def get_current_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role not in (UserRole.ADMIN, UserRole.SUPERUSER):
        raise PermissionError("Admin access required")
    return current_user


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role != UserRole.SUPERUSER:
        raise PermissionError("Superuser access required")
    return current_user


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentAdmin = Annotated[User, Depends(get_current_admin)]
CurrentSuperuser = Annotated[User, Depends(get_current_superuser)]
DBSession = Annotated[AsyncSession, Depends(get_db)]
RedisClient = Annotated[Redis, Depends(get_redis)]
