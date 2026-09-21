from fastapi import HTTPException, status

from app.folders.data.folder_db import FolderDB
from app.folders.data.folders_dao import FoldersDAO
from app.folders.schemas import (
    FolderPostRequest,
    folder_db_to_folder_response,
    FolderPostResponse,
    FolderDeleteResponse,
)
from app.notes.data.notes_dao import NotesDAO
from app.users.data.user_db import UserDB


async def create_or_update_folder(
        request: FolderPostRequest,
        user: UserDB,
) -> FolderPostResponse:
    folder_id = request.folder_id
    folder_db: FolderDB = await FoldersDAO.get_by_id_or_none(folder_id)
    if folder_db is None:
        return await create_new_folder(request, user)
    elif folder_db.owner_id != user.item_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="access denied",
        )
    else:
        return await update_existing_folder(request, user)


async def create_new_folder(
        request: FolderPostRequest,
        user: UserDB,
) -> FolderPostResponse:
    if request.parent_id is not None:
        await _validate_new_parent(request.folder_id, request.parent_id, user)

    folder_db_dict = {
        "item_id": request.folder_id,
        "owner_id": user.item_id,
        "parent_id": request.parent_id,
        "key_id": request.key_id,
        "payload": request.payload,
        "order": request.order,
    }
    folder_db: FolderDB = await FoldersDAO.insert(**folder_db_dict)
    if folder_db:
        return FolderPostResponse(
            message="folder created",
            folder=folder_db_to_folder_response(folder_db),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def update_existing_folder(
        request: FolderPostRequest,
        user: UserDB,
) -> FolderPostResponse:
    if request.parent_id is not None:
        await _validate_new_parent(request.folder_id, request.parent_id, user)

    check = await FoldersDAO.update(
        filter_by={'item_id': request.folder_id},
        parent_id=request.parent_id,
        key_id=request.key_id,
        payload=request.payload,
        order=request.order,
    )
    if check:
        updated_folder_db: FolderDB = await FoldersDAO.get_by_id_or_none(request.folder_id)
        return FolderPostResponse(
            message="folder updated",
            folder=folder_db_to_folder_response(updated_folder_db),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def delete_existing_folder(
        folder_id: str,
        user: UserDB,
) -> FolderDeleteResponse:
    folder_db: FolderDB = await FoldersDAO.get_by_id_or_none(folder_id)
    if folder_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    elif folder_db.owner_id != user.item_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="access denied",
        )
    else:
        folder_and_descendant_ids = await _collect_folder_and_descendants(folder_id)

        for descendant_id in folder_and_descendant_ids:
            await NotesDAO.delete(folder_id=descendant_id)

        check = True
        for descendant_id in reversed(folder_and_descendant_ids):
            deleted_count = await FoldersDAO.delete(item_id=descendant_id)
            if descendant_id == folder_id:
                check = deleted_count

        if check:
            return FolderDeleteResponse(
                message=f"folder with id {folder_id} deleted",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


async def _collect_folder_and_descendants(folder_id: str) -> list[str]:
    ids_in_bfs_order = [folder_id]
    queue = [folder_id]
    while queue:
        current_id = queue.pop(0)
        children = await FoldersDAO.get_all(parent_id=current_id)
        for child in children:
            ids_in_bfs_order.append(child.item_id)
            queue.append(child.item_id)
    return ids_in_bfs_order


async def _validate_new_parent(folder_id: str, parent_id: str, user: UserDB) -> None:
    parent_folder_db: FolderDB = await FoldersDAO.get_by_id_or_none(parent_id)
    if parent_folder_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="parent folder not found",
        )
    if parent_folder_db.owner_id != user.item_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="access denied",
        )
    if await _would_create_cycle(folder_id, parent_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cannot move a folder into its own subtree",
        )


async def _would_create_cycle(folder_id: str, new_parent_id: str) -> bool:
    current_id: str | None = new_parent_id
    while current_id is not None:
        if current_id == folder_id:
            return True
        parent_folder_db: FolderDB = await FoldersDAO.get_by_id_or_none(current_id)
        current_id = parent_folder_db.parent_id if parent_folder_db else None
    return False
