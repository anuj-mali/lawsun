from __future__ import annotations

from starlette.requests import Request

from sqladmin.authentication import AuthenticationBackend

from app.db.redis import get_redis
from app.db.session import AsyncSessionLocal

from app.models.user import UserRole
from app.services.auth import AuthService
from app.repositories import UserRepository, TokenRepository

from app.core.exceptions import AppError


class AdminAuthBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")

        if not email or not password:
            return False

        try:
            async with AsyncSessionLocal() as db:
                redis = await get_redis()
                auth_service = AuthService(
                    user_repo=UserRepository(db), token_repo=TokenRepository(redis)
                )

                result = await auth_service.login(str(email), str(password))

                user_id = auth_service.decode_access_token(result.tokens.access_token)
                user = await UserRepository(db).get_by_id(user_id)

                if not user or user.role != UserRole.SUPERUSER:
                    return False

                request.session["admin_token"] = result.tokens.access_token
            return True
        except AppError:
            return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("admin_token")
        if not token:
            return False

        try:
            async with AsyncSessionLocal() as db:
                redis = await get_redis()
                auth_service = AuthService(
                    user_repo=UserRepository(db), token_repo=TokenRepository(redis)
                )

                user_id = auth_service.decode_access_token(token)
                user = await UserRepository(db).get_by_id(user_id)

                if not user or not user.is_active or user.role != UserRole.SUPERUSER:
                    return False

                return True
        except AppError:
            return False
