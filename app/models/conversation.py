from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import Text, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .user import User
from .base import Base, UUIDMixin, TimestampMixin


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Conversation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str | None] = mapped_column(Text, nullable=True)

    pinned_document_ids: Mapped[list | None] = mapped_column(
        JSONB, nullable=True, default=None
    )

    user: Mapped[User] = relationship(back_populates="conversations", lazy="noload")

    messages: Mapped[list[Message]] = relationship(
        back_populates="conversation",
        lazy="noload",
        order_by="Message.created_at",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Conversation(id={self.id}, title={self.title}, user_id={self.user_id})"


class Message(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[MessageRole] = mapped_column(
        Enum(MessageRole, name="message_role"), nullable=False
    )

    source_chunks: Mapped[list | None] = mapped_column(
        JSONB, nullable=True, default=None
    )

    conversation: Mapped[Conversation] = relationship(
        back_populates="messages", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"Message(id={self.id}, role={self.role!r}, conversation={self.conversation_id})"
