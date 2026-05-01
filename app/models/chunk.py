from __future__ import annotations
from typing import TYPE_CHECKING

import uuid

from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import ForeignKey, Text, Integer, text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pgvector.sqlalchemy import Vector

from app.db.column import BM25Text
from app.db.index import DiskANNIndex, BM25Index

from app.core.config import config

from .base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from .document import Document


class ParentChunk(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "parent_chunks"
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)

    chunk_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Relationships
    document: Mapped[Document] = relationship(
        back_populates="parent_chunks", lazy="noload"
    )
    children: Mapped[list[ChildChunk]] = relationship(
        back_populates="parent", cascade="all, delete-orphan", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"ParentChunk(id={self.id}, document_id={self.document_id}, chunk_index={self.chunk_index})"


class ChildChunk(Base, UUIDMixin):
    __tablename__ = "child_chunks"
    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("parent_chunks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    content: Mapped[str] = mapped_column(BM25Text, nullable=False)
    language: Mapped[str] = mapped_column(String(2), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(
        Vector(config.embedding.dimensions), nullable=False
    )

    chunk_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    parent: Mapped[ParentChunk] = relationship(back_populates="children", lazy="noload")

    __table_args__ = (
        DiskANNIndex(
            "ix_child_chunks_embedding_diskann",
            "embedding",
            num_neighbors=50,
            search_list_size=100,
            max_alpha=1.2,
        ),
        BM25Index(
            "ix_child_chunks_content_bm25_nepali",
            "content",
            text_config="nepali",
            postgresql_where=text("language = 'ne'"),
        ),
        BM25Index(
            "ix_child_chunks_content_bm25_english",
            "content",
            text_config="english",
            postgresql_where=text("language = 'en'"),
        ),
    )
