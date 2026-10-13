from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

SETTING_KEY_MAX_LENGTH = 64


class SettingDB(Base):
    __tablename__ = "user_settings"
    __table_args__ = (
        UniqueConstraint("owner_id", "key", name="uq_user_settings_owner_id_key"),
    )

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.item_id"), nullable=False)
    key: Mapped[str] = mapped_column(String(SETTING_KEY_MAX_LENGTH), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self):
        return f"{self.__class__.__name__}(item_id={self.id})"
