from fastapi import HTTPException, status

from app.folders.data.folder_db import FolderDB
from app.folders.data.folders_dao import FoldersDAO
from app.notes.data.note_db import NoteDB
from app.notes.data.notes_dao import NotesDAO
from app.notes.schemas import NotePostRequest, note_db_to_note_response, NotePostResponse, NoteDeleteResponse
from app.users.data.user_db import UserDB


async def create_or_update_note(
        request: NotePostRequest,
        user: UserDB,
) -> NotePostResponse:
    note_id = request.note_id
    note_db: NoteDB = await NotesDAO.get_by_id_or_none(note_id)
    if note_db is None:
        return await create_new_note(request, user)
    elif note_db.owner_id != user.item_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="access denied",
        )
    else:
        return await update_existing_note(request, user)


async def create_new_note(
        request: NotePostRequest,
        user: UserDB,
) -> NotePostResponse:
    if request.folder_id is not None:
        await _validate_note_folder(request.folder_id, user)

    note_db_dict = {
        "item_id": request.note_id,
        "owner_id": user.item_id,
        "folder_id": request.folder_id,
        "key_id": request.key_id,
        "payload": request.payload,
        "order": request.order,
    }
    note_db: NoteDB = await NotesDAO.insert(**note_db_dict)
    if note_db:
        return NotePostResponse(
            message="note created",
            note=note_db_to_note_response(note_db),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def update_existing_note(
        request: NotePostRequest,
        user: UserDB,
) -> NotePostResponse:
    if request.folder_id is not None:
        await _validate_note_folder(request.folder_id, user)

    check = await NotesDAO.update(
        filter_by={'item_id': request.note_id},
        folder_id=request.folder_id,
        payload=request.payload,
        order=request.order,
    )
    if check:
        updated_note_db: NoteDB = await NotesDAO.get_by_id_or_none(request.note_id)
        return NotePostResponse(
            message="note updated",
            note=note_db_to_note_response(updated_note_db),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def delete_existing_note(
        note_id: str,
        user: UserDB,
) -> NoteDeleteResponse:
    note_db: NoteDB = await NotesDAO.get_by_id_or_none(note_id)
    if note_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    elif note_db.owner_id != user.item_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="access denied",
        )
    else:
        check = await NotesDAO.delete(item_id=note_id)
        if check:
            return NoteDeleteResponse(
                message=f"note with id {note_id} deleted",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


async def _validate_note_folder(folder_id: str, user: UserDB) -> None:
    folder_db: FolderDB = await FoldersDAO.get_by_id_or_none(folder_id)
    if folder_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="folder not found",
        )
    if folder_db.owner_id != user.item_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="access denied",
        )
