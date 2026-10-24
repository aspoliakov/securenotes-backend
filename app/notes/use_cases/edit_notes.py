from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.folders.data.folders_dao import FoldersDAO
from app.notes.data.note_db import NoteDB
from app.notes.data.notes_dao import NotesDAO
from app.notes.schemas import NotePostRequest, note_db_to_note_response, NotePostResponse, NoteDeleteResponse
from app.sync.data.sync_dao import SyncDAO
from app.users.data.user_db import UserDB


async def create_or_update_note(
        request: NotePostRequest,
        user: UserDB,
) -> NotePostResponse:
    async with async_session_maker() as session:
        async with session.begin():
            await SyncDAO.lock(session, user.item_id)
            note_db = await NotesDAO.get_in(session, request.note_id)
            if note_db is None:
                note_db = await create_new_note(session, request, user)
                message = "note created"
            elif note_db.owner_id != user.item_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="access denied",
                )
            elif note_db.deleted_at is not None:
                # deleted on another device: the deletion wins over the edit
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="item already deleted",
                )
            else:
                await update_existing_note(session, request, user, note_db)
                message = "note updated"
            await session.flush()
            # server-side values (dates) are only known after the write
            await session.refresh(note_db)
            return NotePostResponse(
                message=message,
                note=note_db_to_note_response(note_db),
            )


async def create_new_note(
        session: AsyncSession,
        request: NotePostRequest,
        user: UserDB,
) -> NoteDB:
    if request.folder_id is not None:
        await _validate_note_folder(session, request.folder_id, user)

    note_db = NoteDB(
        item_id=request.note_id,
        owner_id=user.item_id,
        folder_id=request.folder_id,
        key_id=request.key_id,
        payload=request.payload,
        order=request.order,
        revision=await SyncDAO.next_revision(session, user.item_id),
    )
    session.add(note_db)
    return note_db


async def update_existing_note(
        session: AsyncSession,
        request: NotePostRequest,
        user: UserDB,
        note_db: NoteDB,
) -> None:
    if request.folder_id is not None:
        await _validate_note_folder(session, request.folder_id, user)

    if _to_utc_millis(request.content_updated_at) != _to_utc_millis(note_db.content_updated_at):
        note_db.content_updated_at = func.now()
    note_db.folder_id = request.folder_id
    note_db.key_id = request.key_id
    note_db.payload = request.payload
    note_db.order = request.order
    note_db.revision = await SyncDAO.next_revision(session, user.item_id)


async def delete_existing_note(
        note_id: str,
        user: UserDB,
) -> NoteDeleteResponse:
    async with async_session_maker() as session:
        async with session.begin():
            await SyncDAO.lock(session, user.item_id)
            note_db = await NotesDAO.get_in(session, note_id)
            if note_db is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            elif note_db.owner_id != user.item_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="access denied",
                )
            elif note_db.deleted_at is None:
                # a repeated delete leaves the note as it is: the client retries until it succeeds
                values = SyncDAO.tombstone_values(await SyncDAO.next_revision(session, user.item_id))
                for key, value in values.items():
                    setattr(note_db, key, value)
    return NoteDeleteResponse(
        message=f"note with id {note_id} deleted",
    )


async def _validate_note_folder(session: AsyncSession, folder_id: str, user: UserDB) -> None:
    folder_db = await FoldersDAO.get_in(session, folder_id)
    if folder_db is None or folder_db.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="folder not found",
        )
    if folder_db.owner_id != user.item_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="access denied",
        )


def _to_utc_millis(value: datetime) -> datetime:
    """Naive UTC truncated to milliseconds: the client keeps timestamps in epoch millis."""
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return value.replace(microsecond=value.microsecond // 1000 * 1000)
