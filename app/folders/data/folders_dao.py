from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.data.base_dao import BaseDAO
from app.folders.data.folder_db import FolderDB


class FoldersDAO(BaseDAO):
    model = FolderDB

    @classmethod
    async def get_in(cls, session: AsyncSession, item_id: str) -> FolderDB | None:
        return await session.scalar(select(cls.model).filter_by(item_id=item_id))

    @classmethod
    async def get_children_in(cls, session: AsyncSession, parent_id: str) -> list[FolderDB]:
        result = await session.execute(select(cls.model).filter_by(parent_id=parent_id))
        return list(result.scalars().all())

    @classmethod
    async def delete_many(cls, session: AsyncSession, folder_ids: list[str], values: dict) -> None:
        query = (
            sqlalchemy_update(cls.model)
            .where(cls.model.item_id.in_(folder_ids), cls.model.deleted_at.is_(None))
            .values(**values)
        )
        await session.execute(query)
