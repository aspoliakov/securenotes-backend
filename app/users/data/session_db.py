from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

# hex-encoded SHA-256
TOKEN_HASH_LENGTH = 64


class SessionDB(Base):
    """One signed-in device. Access tokens reference it by item_id, so deleting the row revokes them all."""
    __tablename__ = "user_sessions"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.item_id"), nullable=False, index=True)
    refresh_token_hash: Mapped[str] = mapped_column(String(TOKEN_HASH_LENGTH), unique=True, nullable=False)
    # the rotated-out refresh token, kept to tell a retried refresh from a stolen token being replayed
    previous_refresh_token_hash: Mapped[str | None] = mapped_column(String(TOKEN_HASH_LENGTH), index=True)
    rotated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"{self.__class__.__name__}(item_id={self.id})"
