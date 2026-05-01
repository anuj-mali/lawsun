from __future__ import annotations

import uuid

from app.models.legal_body import Ministry
from app.repositories.ministry import MinistryRepository

from app.core.exceptions import DuplicateMinistryError, MinistryNotFoundError


class MinistryService:
    def __init__(self, repo: MinistryRepository) -> None:
        self.repo = repo

    async def create(
        self,
        *,
        name: str,
        short_name: str | None = None,
        description: str | None = None,
    ) -> Ministry:
        existing = await self.repo.get_by_name(name)
        if existing is not None:
            raise DuplicateMinistryError()

        return await self.repo.create(
            name=name, short_name=short_name, description=description
        )

    async def update(self, ministry_id: uuid.UUID, **fields) -> Ministry:
        ministry = await self.repo.get_by_id(ministry_id)

        if ministry is None:
            raise MinistryNotFoundError()

        new_name = fields.get("name")
        if new_name and new_name != ministry.name:
            existing = await self.repo.get_by_name(new_name)
            if existing is not None:
                raise DuplicateMinistryError()

        return await self.repo.update(ministry, **fields)

    async def deactivate(self, ministry_id: uuid.UUID) -> Ministry:
        ministry = await self.repo.get_by_id(ministry_id)
        if ministry is None:
            raise MinistryNotFoundError()

        return await self.repo.deactivate(ministry)

    async def hard_delete(self, ministry_id: uuid.UUID) -> None:
        ministry = await self.repo.get_by_id(ministry_id)
        if ministry is None:
            raise MinistryNotFoundError()

        await self.repo.hard_delete(ministry)

    async def get(self, ministry_id: uuid.UUID) -> Ministry:
        ministry = await self.repo.get_by_id(ministry_id)
        if ministry is None:
            raise MinistryNotFoundError()

        return ministry

    async def get_all(
        self,
        *,
        page_size: int = 20,
        cursor: uuid.UUID | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[Ministry], uuid.UUID | None]:
        return await self.repo.get_all(
            page_size=page_size, cursor=cursor, is_active=is_active
        )
