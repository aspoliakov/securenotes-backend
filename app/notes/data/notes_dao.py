from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.data.base_dao import BaseDAO
from app.notes.data.note_db import NoteDB


class NotesDAO(BaseDAO):
    model = NoteDB

    @classmethod
    async def get_in(cls, session: AsyncSession, item_id: str) -> NoteDB | None:
        return await session.scalar(select(cls.model).filter_by(item_id=item_id))

    @classmethod
    async def delete_in_folders(cls, session: AsyncSession, folder_ids: list[str], values: dict) -> None:
        query = (
            sqlalchemy_update(cls.model)
            .where(cls.model.folder_id.in_(folder_ids), cls.model.deleted_at.is_(None))
            .values(**values)
        )
        await session.execute(query)
