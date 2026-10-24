from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.folders.data.folder_db import FolderDB
from app.folders.data.folders_dao import FoldersDAO
from app.folders.schemas import (
    FolderPostRequest,
    folder_db_to_folder_response,
    FolderPostResponse,
    FolderDeleteResponse,
)
from app.notes.data.notes_dao import NotesDAO
from app.sync.data.sync_dao import SyncDAO
from app.users.data.user_db import UserDB


async def create_or_update_folder(
        request: FolderPostRequest,
        user: UserDB,
) -> FolderPostResponse:
    async with async_session_maker() as session:
        async with session.begin():
            await SyncDAO.lock(session, user.item_id)
            folder_db = await FoldersDAO.get_in(session, request.folder_id)
            if folder_db is None:
                folder_db = await create_new_folder(session, request, user)
                message = "folder created"
            elif folder_db.owner_id != user.item_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="access denied",
                )
            elif folder_db.deleted_at is not None:
                # deleted on another device: the deletion wins over the edit
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="item already deleted",
                )
            else:
                await update_existing_folder(session, request, user, folder_db)
                message = "folder updated"
            await session.flush()
            # server-side values (dates) are only known after the write
            await session.refresh(folder_db)
            return FolderPostResponse(
                message=message,
                folder=folder_db_to_folder_response(folder_db),
            )


async def create_new_folder(
        session: AsyncSession,
        request: FolderPostRequest,
        user: UserDB,
) -> FolderDB:
    if request.parent_id is not None:
        await _validate_new_parent(session, request.folder_id, request.parent_id, user)

    folder_db = FolderDB(
        item_id=request.folder_id,
        owner_id=user.item_id,
        parent_id=request.parent_id,
        key_id=request.key_id,
        payload=request.payload,
        order=request.order,
        revision=await SyncDAO.next_revision(session, user.item_id),
    )
    session.add(folder_db)
    return folder_db


async def update_existing_folder(
        session: AsyncSession,
        request: FolderPostRequest,
        user: UserDB,
        folder_db: FolderDB,
) -> None:
    if request.parent_id is not None:
        await _validate_new_parent(session, request.folder_id, request.parent_id, user)

    folder_db.parent_id = request.parent_id
    folder_db.key_id = request.key_id
    folder_db.payload = request.payload
    folder_db.order = request.order
    folder_db.revision = await SyncDAO.next_revision(session, user.item_id)


async def delete_existing_folder(
        folder_id: str,
        user: UserDB,
) -> FolderDeleteResponse:
    async with async_session_maker() as session:
        async with session.begin():
            await SyncDAO.lock(session, user.item_id)
            folder_db = await FoldersDAO.get_in(session, folder_id)
            if folder_db is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            elif folder_db.owner_id != user.item_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="access denied",
                )
            elif folder_db.deleted_at is None:
                # a repeated delete leaves the folder as it is: the client retries until it succeeds
                folder_and_descendant_ids = await _collect_folder_and_descendants(session, folder_id)
                values = SyncDAO.tombstone_values(await SyncDAO.next_revision(session, user.item_id))
                await NotesDAO.delete_in_folders(session, folder_and_descendant_ids, values)
                await FoldersDAO.delete_many(session, folder_and_descendant_ids, values)
    return FolderDeleteResponse(
        message=f"folder with id {folder_id} deleted",
    )


async def _collect_folder_and_descendants(session: AsyncSession, folder_id: str) -> list[str]:
    ids_in_bfs_order = [folder_id]
    queue = [folder_id]
    while queue:
        current_id = queue.pop(0)
        children = await FoldersDAO.get_children_in(session, current_id)
        for child in children:
            ids_in_bfs_order.append(child.item_id)
            queue.append(child.item_id)
    return ids_in_bfs_order


async def _validate_new_parent(session: AsyncSession, folder_id: str, parent_id: str, user: UserDB) -> None:
    parent_folder_db = await FoldersDAO.get_in(session, parent_id)
    if parent_folder_db is None or parent_folder_db.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="parent folder not found",
        )
    if parent_folder_db.owner_id != user.item_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="access denied",
        )
    if await _would_create_cycle(session, folder_id, parent_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cannot move a folder into its own subtree",
        )


async def _would_create_cycle(session: AsyncSession, folder_id: str, new_parent_id: str) -> bool:
    current_id: str | None = new_parent_id
    while current_id is not None:
        if current_id == folder_id:
            return True
        parent_folder_db = await FoldersDAO.get_in(session, current_id)
        current_id = parent_folder_db.parent_id if parent_folder_db else None
    return False
