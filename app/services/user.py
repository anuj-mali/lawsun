from __future__ import annotations

from sqlalchemy.exc import IntegrityError

from app.repositories import UserRepository

import uuid

from app.models.user import User, UserRole
from app.core.exceptions import (
    DuplicateEmailError,
    UserNotFoundError,
    SelfDeactivationError,
    ForbiddenError,
)


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()
        return user

    async def get_by_email(self, email: str) -> User:
        user = await self.repo.get_by_email(email)
        if user is None:
            raise UserNotFoundError()
        return user

    async def get_all(
        self,
        page_size: int = 20,
        cursor: uuid.UUID | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[User], uuid.UUID | None]:
        return await self.repo.get_all(
            page_size=page_size, cursor=cursor, is_active=is_active
        )

    async def create(
        self,
        requester: User,
        email: str,
        hashed_password: str,
        first_name: str,
        last_name: str,
        middle_name: str | None = None,
        role: UserRole = UserRole.USER,
    ) -> User:
        if role in (UserRole.ADMIN, UserRole.SUPERUSER):
            if requester.role != UserRole.SUPERUSER:
                raise ForbiddenError("Only superusers can create privileged users")

        existing = await self.repo.get_by_email(email)
        if existing is not None:
            raise DuplicateEmailError()

        try:
            return await self.repo.create(
                email=email,
                hashed_password=hashed_password,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                role=role,
            )
        except IntegrityError:
            raise DuplicateEmailError()

    async def update(self, user_id: uuid.UUID, **kwargs) -> User:
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()

        return await self.repo.update(user, **kwargs)

    async def deactivate(self, user_id: uuid.UUID, requester: User) -> User:
        if requester.id == user_id:
            raise SelfDeactivationError()

        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()

        if user.role in (UserRole.ADMIN, UserRole.SUPERUSER):
            if requester.role != UserRole.SUPERUSER:
                raise ForbiddenError("Only superusers can deactivate privileged users")

        return await self.repo.deactivate(user)
