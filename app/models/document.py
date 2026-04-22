import uuid

from enum import StrEnum

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, Enum, ForeignKey, String, Integer, UniqueConstraint

from .chunk import ParentChunk
from .legal_body import Ministry
from .base import Base, UUIDMixin, TimestampMixin


class DocumentStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class DocumentCategory(StrEnum):
    CONSTITUTION = "constitution"
    ACT = "act"
    REGULATION = "regulation"
    AMENDMENT = "amendment"
    ORDINANCE = "ordinance"
    GUIDELINE = "guideline"
    OTHER = "other"


class Language(StrEnum):
    ENGLISH = "en"
    NEPALI = "ne"


class Document(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(Text, nullable=False)

    category: Mapped[DocumentCategory] = mapped_column(
        Enum(DocumentCategory, name="document_category"),
        nullable=False,
    )
    language: Mapped[Language] = mapped_column(
        Enum(Language, name="language"), nullable=False, default=Language.NEPALI
    )
    ministry_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ministries.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    domain: Mapped[str | None] = mapped_column(String(100), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)

    # Deduplication
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    # Ingestion Status
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, name="document_status"),
        nullable=False,
        default=DocumentStatus.PENDING,
        index=True,
    )
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    ministry: Mapped[Ministry | None] = relationship(lazy="noload")
    parent_chunks: Mapped[list[ParentChunk]] = relationship(
        back_populates="document", cascade="all, delete-orphan", lazy="noload"
    )

    __table_args__ = (
        UniqueConstraint(
            "file_hash",
            name="uq_file_hash",
        ),
    )

    def __repr__(self) -> str:
        return f"Document(id={self.id}, title={self.title!r}, category={self.category!r}, language={self.language!r}, ministry_id={self.ministry_id})"
