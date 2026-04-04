from enum import StrEnum

from sqlalchemy import String, Boolean, Enum
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, UUIDMixin, TimestampMixin


class UserRole(StrEnum):
    SUPERUSER = "superuser"
    ADMIN = "admin"
    USER = "user"


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        CITEXT, nullable=False, index=True, unique=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False, default=UserRole.USER)

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email}, role={self.role})"
