from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

# hex-encoded SHA-256
TOKEN_HASH_LENGTH = 64

DEVICE_NAME_LENGTH = 128
PLATFORM_LENGTH = 16
OS_VERSION_LENGTH = 32


class SessionDB(Base):
    """One signed-in device. Access tokens reference it by item_id, so deleting the row revokes them all."""
    __tablename__ = "user_sessions"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.item_id"), nullable=False, index=True)
    refresh_token_hash: Mapped[str] = mapped_column(String(TOKEN_HASH_LENGTH), unique=True, nullable=False)
    previous_refresh_token_hash: Mapped[str | None] = mapped_column(String(TOKEN_HASH_LENGTH), index=True)
    rotated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    device_name: Mapped[str | None] = mapped_column(String(DEVICE_NAME_LENGTH))
    platform: Mapped[str | None] = mapped_column(String(PLATFORM_LENGTH))
    os_version: Mapped[str | None] = mapped_column(String(OS_VERSION_LENGTH))

    def __repr__(self):
        return f"{self.__class__.__name__}(item_id={self.id})"
