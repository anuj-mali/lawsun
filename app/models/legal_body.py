from .base import Base, UUIDMixin, TimestampMixin

from sqlalchemy import Text, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column


class Ministry(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ministries"

    name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, unique=True
    )
    short_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"Ministry(id={self.id}, name={self.name!r})"
