from __future__ import annotations

from sqladmin import ModelView

from app.models.user import User
from app.models.document import Document
from app.models.legal_body import Ministry
from app.models.chunk import ParentChunk, ChildChunk
from app.models.conversation import Conversation, Message


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-users"

    column_list = [
        User.id,
        User.email,
        User.first_name,
        User.middle_name,
        User.last_name,
        User.role,
        User.is_active,
        User.created_at,
    ]

    column_searchable_list = [
        User.email,
        User.first_name,
        User.middle_name,
        User.last_name,
    ]

    column_sortable_list = [
        User.email,
        User.role,
        User.is_active,
        User.created_at,
    ]

    column_filters = [
        User.role,
        User.is_active,
    ]

    form_excluded_columns = [User.hashed_password]
    column_details_list = [User.hashed_password]

    can_create = False
    can_delete = False


class MinistryAdmin(ModelView, model=Ministry):
    name = "Ministry"
    name_plural = "Ministries"
    icon = "fa-solid fa-building-columns"

    column_list = [
        Ministry.id,
        Ministry.name,
        Ministry.short_name,
        Ministry.is_active,
        Ministry.created_at,
    ]

    column_searchable_list = [
        Ministry.name,
        Ministry.short_name,
    ]

    column_sortable_list = [
        Ministry.name,
        Ministry.is_active,
        Ministry.created_at,
    ]
    column_sortable_list = [
        Ministry.name,
        Ministry.is_active,
        Ministry.created_at,
    ]

    column_filters = [
        Ministry.is_active,
    ]


class DocumentAdmin(ModelView, model=Document):
    name = "Document"
    name_plural = "Documents"
    icon = "fa-solid fa-file-lines"

    column_list = [
        Document.id,
        Document.title,
        Document.category,
        Document.language,
        Document.ministry_id,
        Document.year,
        Document.status,
        Document.created_at,
    ]

    column_searchable_list = [Document.title, Document.category, Document.source_url]

    column_sortable_list = [
        Document.title,
        Document.category,
        Document.language,
        Document.year,
        Document.status,
        Document.created_at,
    ]

    column_filters = [
        Document.category,
        Document.language,
        Document.status,
    ]
    can_create = False
    can_delete = True


class ParentChunkAdmin(ModelView, model=ParentChunk):
    name = "Chunk"
    name_plural = "Chunks"
    icon = "fa-solid fa-layer-group"

    column_list = [
        ParentChunk.id,
        ParentChunk.document_id,
        ParentChunk.chunk_index,
        ParentChunk.created_at,
    ]

    column_sortable_list = [
        ParentChunk.chunk_index,
        ParentChunk.created_at,
    ]

    column_filters = [
        ParentChunk.document_id,
    ]

    column_details_list = [
        ParentChunk.id,
        ParentChunk.document_id,
        ParentChunk.chunk_index,
        ParentChunk.content,
        ParentChunk.chunk_metadata,
        ParentChunk.children,
        ParentChunk.created_at,
    ]

    can_create = False
    can_edit = False


class ChildChunkAdmin(ModelView, model=ChildChunk):
    name = "Child Chunk"
    name_plural = "Child Chunks"

    column_list = [
        ChildChunk.id,
        ChildChunk.parent_id,
        ChildChunk.chunk_index,
        ChildChunk.language,
        ChildChunk.content,
    ]

    column_details_exclude_list = [
        ChildChunk.embedding,
    ]

    can_create = False
    can_edit = False


class ConversationAdmin(ModelView, model=Conversation):
    name = "Conversation"
    name_plural = "Conversations"
    icon = "fa-solid fa-comments"

    column_list = [
        Conversation.id,
        Conversation.user_id,
        Conversation.title,
        Conversation.created_at,
    ]

    column_searchable_list = [
        Conversation.title,
    ]

    column_sortable_list = [
        Conversation.created_at,
    ]

    column_details_list = [
        Conversation.id,
        Conversation.user_id,
        Conversation.title,
        Conversation.pinned_document_ids,
        Conversation.messages,
        Conversation.created_at,
        Conversation.updated_at,
    ]

    can_create = False
    can_delete = False


class MessageAdmin(ModelView, model=Message):
    name = "Message"
    name_plural = "Messages"

    column_list = [
        Message.id,
        Message.role,
        Message.content,
        Message.created_at,
    ]

    can_create = False
    can_edit = False
