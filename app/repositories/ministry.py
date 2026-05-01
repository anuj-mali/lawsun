from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exceptions import InvalidCursorError
from app.models.legal_body import Ministry

import uuid


class MinistryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, ministry_id: uuid.UUID) -> Ministry | None:
        return await self.db.get(Ministry, ministry_id)

    async def get_by_name(self, name: str) -> Ministry | None:
        result = await self.db.execute(select(Ministry).where(Ministry.name == name))
        return result.scalar_one_or_none()

    async def create(
        self, name: str, short_name: str | None = None, description: str | None = None
    ) -> Ministry:
        ministry = Ministry(
            name=name,
            short_name=short_name,
            description=description,
        )
        self.db.add(ministry)
        await self.db.flush()
        return ministry

    async def update(self, ministry: Ministry, **kwargs) -> Ministry:
        for key, value in kwargs.items():
            setattr(ministry, key, value)
        await self.db.flush()
        return ministry

    async def deactivate(self, ministry: Ministry) -> Ministry:
        return await self.update(ministry, is_active=False)

    async def hard_delete(self, ministry: Ministry) -> None:
        await self.db.delete(ministry)
        await self.db.flush()

    async def get_all(
        self,
        *,
        page_size: int = 20,
        cursor: uuid.UUID | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[Ministry], uuid.UUID | None]:
        stmt = select(Ministry).order_by(Ministry.created_at.desc(), Ministry.id.desc())

        if is_active is not None:
            stmt = stmt.where(Ministry.is_active == is_active)

        if cursor is not None:
            cursor_ministry = await self.get_by_id(cursor)
            if cursor_ministry is None:
                raise InvalidCursorError()

            stmt = stmt.where(
                (Ministry.created_at < cursor_ministry.created_at)
                | (
                    (Ministry.created_at == cursor_ministry.created_at)
                    & (Ministry.id < cursor_ministry.id)
                )
            )

        result = await self.db.execute(stmt.limit(page_size + 1))

        ministries = list(result.scalars().all())

        next_cursor: uuid.UUID | None = None
        if len(ministries) > page_size:
            ministries = ministries[:page_size]
            next_cursor = ministries[-1].id

        return ministries, next_cursor
