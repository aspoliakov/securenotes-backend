from datetime import datetime

from sqlalchemy import delete as sqlalchemy_delete, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from app.data.base_dao import BaseDAO
from app.database import async_session_maker
from app.users.data.session_db import SessionDB


class SessionsDAO(BaseDAO):
    model = SessionDB

    @classmethod
    async def get_by_refresh_token_hash(cls, token_hash: str):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(refresh_token_hash=token_hash)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_by_previous_refresh_token_hash(cls, token_hash: str):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(previous_refresh_token_hash=token_hash)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def delete_by_refresh_token_hash(cls, token_hash: str):
        await cls._delete_where(
            or_(
                cls.model.refresh_token_hash == token_hash,
                cls.model.previous_refresh_token_hash == token_hash,
            )
        )

    @classmethod
    async def delete_expired(cls, owner_id: str, now: datetime):
        await cls._delete_where(
            cls.model.owner_id == owner_id,
            cls.model.expires_at < now,
        )

    @classmethod
    async def _delete_where(cls, *conditions):
        async with async_session_maker() as session:
            async with session.begin():
                query = sqlalchemy_delete(cls.model).where(*conditions)
                result = await session.execute(query)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return result.rowcount
