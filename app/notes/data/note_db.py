from datetime import datetime

from sqlalchemy import Float, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NoteDB(Base):
    __tablename__ = "notes"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.item_id"), nullable=False)
    folder_id: Mapped[str | None] = mapped_column(ForeignKey("folders.item_id"), nullable=True)
    key_id: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[float] = mapped_column("order_index", Float, nullable=False, server_default="0")
    # moves only when the client reports a content change; updated_at is technical and moves on any update
    content_updated_at: Mapped[datetime] = mapped_column(server_default=func.now())

    def __repr__(self):
        return f"{self.__class__.__name__}(item_id={self.id})"
