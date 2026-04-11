from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import AnyHttpUrl, Field

from app.models.document import DocumentCategory, DocumentStatus, Language

from .base import AppSchema


class DocumentCreate(AppSchema):
    title: str = Field(min_length=1, max_length=255)
    source_url: AnyHttpUrl
    category: DocumentCategory
    language: Language = Language.NEPALI
    ministry_id: uuid.UUID | None = None
    domain: str | None = Field(min_length=1, max_length=100)
    year: int | None = Field(ge=1900, le=2100)


class DocumentUpdate(AppSchema):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    category: DocumentCategory | None = None
    language: Language | None = None
    ministry_id: uuid.UUID | None = None
    domain: str | None = Field(default=None, min_length=1, max_length=100)
    year: int | None = Field(default=None, ge=1900, le=2100)


class DocumentReingest(AppSchema):
    force: bool = False


class MinistryResponse(AppSchema):
    id: uuid.UUID
    name: str
    short_name: str | None


class DocumentResponse(AppSchema):
    id: uuid.UUID
    title: str
    category: DocumentCategory
    language: Language
    ministry: MinistryResponse | None
    domain: str | None
    year: int | None
    source_url: AnyHttpUrl
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(AppSchema):
    id: uuid.UUID
    title: str
    category: DocumentCategory
    language: Language
    ministry_id: uuid.UUID | None
    domain: str | None
    year: int | None
    status: DocumentStatus
    created_at: datetime


class DocumentListPageResponse(AppSchema):
    items: list[DocumentListResponse]
    total: int
    page: int
    page_size: int


class DocumentIngestionStatusResponse(AppSchema):
    id: uuid.UUID
    status: DocumentStatus
    celery_task_id: str | None
