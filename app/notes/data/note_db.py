from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NoteDB(Base):
    __tablename__ = "notes"
    __table_args__ = (
        Index("ix_notes_owner_id_revision", "owner_id", "revision"),
    )

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.item_id"), nullable=False)
    folder_id: Mapped[str | None] = mapped_column(ForeignKey("folders.item_id"), nullable=True)
    key_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    order: Mapped[float] = mapped_column("order_index", Float, nullable=False, server_default="0")
    content_updated_at: Mapped[datetime] = mapped_column(server_default=func.now())
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(item_id={self.id})"
