from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FolderDB(Base):
    __tablename__ = "folders"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.item_id"), nullable=False)
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("folders.item_id"), nullable=True)
    key_id: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self):
        return f"{self.__class__.__name__}(item_id={self.id})"
