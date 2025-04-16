from pydantic import EmailStr
from sqlalchemy.future import select

from app.data.base_dao import BaseDAO
from app.database import async_session_maker
from app.users.data.user_db import UserDB


class UsersDAO(BaseDAO):
    model = UserDB

    @classmethod
    async def get_by_email(cls, email: EmailStr):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(email=email)
            result = await session.execute(query)
            return result.scalar_one_or_none()
