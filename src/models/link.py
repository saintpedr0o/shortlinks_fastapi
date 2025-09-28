from typing import List
import uuid
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime, timezone
from src.config import get_settings

settings = get_settings()


class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(primary_key=True)
    original_link: Mapped[str] = mapped_column(nullable=False)
    short_code: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Many-to-one: Links -> User
    user: Mapped["User"] = relationship(back_populates="links")  # type: ignore
    # One-to-many: Link -> Clicks
    clicks: Mapped[List["Click"]] = relationship(  # type: ignore
        back_populates="link", cascade="all, delete-orphan"
    )

    @property
    def short_url(self) -> str:
        prefix_part = f"/{settings.redirect_prefix}" if settings.redirect_prefix else ""
        return f"{settings.base_url}{prefix_part}/{self.short_code}"
