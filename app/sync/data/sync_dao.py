from datetime import datetime

from sqlalchemy import delete as sqlalchemy_delete, func, update as sqlalchemy_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.folders.data.folder_db import FolderDB
from app.notes.data.note_db import NoteDB
from app.users.data.session_db import SessionDB
from app.users.data.user_db import UserDB


class SyncDAO:
    """
    Revisions of a user's notes and folders. A write locks the owner's row first and takes the next
    revision before committing, so a user's writes run one at a time and revisions follow the commit order:
    a client that got revision N has seen every change up to N.
    """

    @staticmethod
    async def lock(session: AsyncSession, owner_id: str) -> None:
        """Locks the owner's data until the transaction ends. Call before reading what is going to be changed."""
        await session.execute(select(UserDB.id).where(UserDB.item_id == owner_id).with_for_update())

    @staticmethod
    async def next_revision(session: AsyncSession, owner_id: str) -> int:
        query = (
            sqlalchemy_update(UserDB)
            .where(UserDB.item_id == owner_id)
            .values(sync_revision=UserDB.sync_revision + 1)
            .returning(UserDB.sync_revision)
        )
        return (await session.execute(query)).scalar_one()

    @staticmethod
    def tombstone_values(revision: int) -> dict:
        """Deletes a note or a folder: only the ids, the place and the dates are left."""
        return {
            "deleted_at": func.now(),
            "key_id": None,
            "payload": None,
            "revision": revision,
        }

    @staticmethod
    async def get_revision(session: AsyncSession, owner_id: str) -> int:
        return await session.scalar(select(UserDB.sync_revision).where(UserDB.item_id == owner_id))

    @staticmethod
    async def get_changed(session: AsyncSession, model, owner_id: str, since: int | None) -> list:
        """Changed after since, deleted ones included; with no since every existing one, as a first sync."""
        query = select(model).where(model.owner_id == owner_id)
        if since is None:
            query = query.where(model.deleted_at.is_(None))
        else:
            query = query.where(model.revision > since)
        return list((await session.execute(query)).scalars().all())

    @staticmethod
    async def save_session_revision(session: AsyncSession, session_id: str, revision: int) -> None:
        query = (
            sqlalchemy_update(SessionDB)
            .where(SessionDB.item_id == session_id)
            .values(synced_revision=revision)
        )
        await session.execute(query)

    @staticmethod
    async def get_min_session_revision(session: AsyncSession, owner_id: str, now: datetime) -> int | None:
        """The oldest revision an active device has applied; devices that have never synced don't count."""
        query = select(func.min(SessionDB.synced_revision)).where(
            SessionDB.owner_id == owner_id,
            SessionDB.expires_at >= now,
            SessionDB.synced_revision.is_not(None),
        )
        return await session.scalar(query)

    @staticmethod
    async def delete_tombstones(session: AsyncSession, owner_id: str, up_to_revision: int) -> None:
        # notes first: they reference folders
        for model in (NoteDB, FolderDB):
            query = sqlalchemy_delete(model).where(
                model.owner_id == owner_id,
                model.deleted_at.is_not(None),
                model.revision <= up_to_revision,
            )
            await session.execute(query)
