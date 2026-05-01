from __future__ import annotations

import uuid
from pydantic import Field
from datetime import datetime

from .base import AppSchema


class MinistryCreate(AppSchema):
    name: str = Field(min_length=1, max_length=255)
    short_name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    is_active: bool = True


class MinistryUpdate(AppSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    short_name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    is_active: bool | None = None


class MinistryResponse(AppSchema):
    id: uuid.UUID
    name: str
    short_name: str | None
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MinistryListResponse(AppSchema):
    items: list[MinistryResponse]
    next_cursor: uuid.UUID | None
