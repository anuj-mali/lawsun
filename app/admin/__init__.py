from __future__ import annotations

from sqladmin import Admin

from fastapi import FastAPI

from app.db.session import engine
from app.core.config import config

from .auth import AdminAuthBackend
from .views import (
    UserAdmin,
    MinistryAdmin,
    DocumentAdmin,
    ParentChunkAdmin,
    ConversationAdmin,
    MessageAdmin,
    ChildChunkAdmin,
)


def setup_admin(app: FastAPI) -> None:
    admin = Admin(
        app=app,
        engine=engine,
        title="Lawsun Admin",
        base_url="/admin",
        authentication_backend=AdminAuthBackend(secret_key=config.auth.secret_key),
    )

    admin.add_view(UserAdmin)
    admin.add_view(MinistryAdmin)
    admin.add_view(DocumentAdmin)
    admin.add_view(ParentChunkAdmin)
    admin.add_view(ConversationAdmin)

    admin.add_view(MessageAdmin)
    admin.add_view(ChildChunkAdmin)
