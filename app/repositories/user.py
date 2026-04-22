from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User, UserRole

from app.core.exceptions import InvalidCursorError

import uuid


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.db.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(
        self,
        email: str,
        hashed_password: str,
        first_name: str,
        last_name: str,
        middle_name: str | None = None,
        role: UserRole = UserRole.USER,
    ) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            role=role,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def update(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            setattr(user, key, value)
        await self.db.flush()
        return user

    async def deactivate(self, user: User) -> User:
        return await self.update(user, is_active=False)

    async def hard_delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.flush()

    async def get_all(
        self,
        *,
        page_size: int = 20,
        cursor: uuid.UUID | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[User], uuid.UUID | None]:
        stmt = select(User).order_by(User.created_at.desc(), User.id.desc())

        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)

        if cursor is not None:
            cursor_user = await self.get_by_id(cursor)
            if cursor_user is None:
                raise InvalidCursorError()

            stmt = stmt.where(
                (User.created_at < cursor_user.created_at)
                | (
                    (User.created_at == cursor_user.created_at)
                    & (User.id < cursor_user.id)
                )
            )

        result = await self.db.execute(stmt.limit(page_size + 1))

        users = list(result.scalars().all())

        next_cursor: uuid.UUID | None = None
        if len(users) > page_size:
            users = users[:page_size]
            next_cursor = users[-1].id

        return users, next_cursor
