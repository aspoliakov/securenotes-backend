import enum

from sqlalchemy import Text, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, str_uniq, str_uniq_nullable


class Role(enum.Enum):
    admin = 0
    user = 1


class UserDB(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("provider", "provider_id", name="uq_users_provider_provider_id"),
    )

    email: Mapped[str_uniq]
    login: Mapped[str_uniq_nullable]
    password: Mapped[str | None]
    role: Mapped[Role] = mapped_column(Enum(Role, name='user_role'), nullable=False, default=Role.user)
    avatar: Mapped[str] = mapped_column(Text, nullable=True)
    provider: Mapped[str | None]
    provider_id: Mapped[str | None]

    def __repr__(self):
        return f"{self.__class__.__name__}(item_id={self.id})"
