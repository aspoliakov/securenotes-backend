from sqlalchemy import ForeignKey, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class KeyDB(Base):
    __tablename__ = "keys"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.item_id"), nullable=False)
    public_key: Mapped[str] = mapped_column(Text, nullable=False)
    encrypted_private_key: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Numeric, nullable=False)

    def __repr__(self):
        return f"{self.__class__.__name__}(item_id={self.id})"
