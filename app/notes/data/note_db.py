from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NoteDB(Base):
    __tablename__ = "notes"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.item_id"), nullable=False)
    key_id: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self):
        return f"{self.__class__.__name__}(item_id={self.id})"
