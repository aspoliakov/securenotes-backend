import enum

from sqlalchemy import Text, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, str_uniq, str_uniq_nullable


class Role(enum.Enum):
    admin = 0
    user = 1


class UserDB(Base):
    __tablename__ = "users"

    email: Mapped[str_uniq]
    login: Mapped[str_uniq_nullable]
    password: Mapped[str]
    role: Mapped[Role] = mapped_column(Enum(Role, name='user_role'), nullable=False, default=Role.user)
    avatar: Mapped[str] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(item_id={self.id})"
