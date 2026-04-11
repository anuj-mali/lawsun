from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import Field, AnyHttpUrl

from app.models.conversation import MessageRole

from .base import AppSchema


class SourceChunk(AppSchema):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_title: str
    source_url: AnyHttpUrl
    content: str
    distance: float


class MessageResponse(AppSchema):
    id: uuid.UUID
    role: MessageRole
    content: str
    source_chunks: list[SourceChunk] | None = None
    created_at: datetime


class ConversationCreate(AppSchema):
    title: str | None = Field(default=None, max_length=255)
    pinned_document_ids: list[uuid.UUID] | None = None


class ConversationUpdate(AppSchema):
    title: str | None = Field(default=None, max_length=255)
    pinned_document_ids: list[uuid.UUID] | None = None


class ConversationResponse(AppSchema):
    id: uuid.UUID
    title: str | None
    pinned_document_ids: list[uuid.UUID] | None
    messages: list[MessageResponse]
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(AppSchema):
    id: uuid.UUID
    title: str | None
    pinned_document_ids: list[uuid.UUID] | None
    created_at: datetime
    updated_at: datetime


class ConversationListPageResponse(AppSchema):
    items: list[ConversationListResponse]
    total: int
    page: int
    page_size: int


class QueryRequest(AppSchema):
    message: str = Field(min_length=1, max_length=1000)


class QueryResponse(AppSchema):
    user_message: MessageResponse
    assistant_message: MessageResponse
