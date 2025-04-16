from fastapi import APIRouter
from fastapi.params import Depends

from app.notes.schemas import NotePostRequest, NotesGetResponse, NotePostResponse, NoteDeleteResponse
from app.notes.use_cases.edit_notes import delete_existing_note, create_or_update_note
from app.notes.use_cases.get_notes import get_all
from app.users.data.user_db import UserDB
from app.users.dependencies import get_user_by_token

router = APIRouter(prefix='/api/v1/notes', tags=["Notes public route"])


@router.get("/all", summary="Get all User notes")
async def get_all_notes(
        user: UserDB = Depends(get_user_by_token),
) -> NotesGetResponse:
    return await get_all(user)


@router.post("/save", summary="Create User note with full JSON")
async def save_note(
        request: NotePostRequest,
        user: UserDB = Depends(get_user_by_token),
) -> NotePostResponse:
    return await create_or_update_note(request, user)


@router.delete("/{note_id}", summary="Delete User note by id")
async def delete_note(
        note_id: str,
        user: UserDB = Depends(get_user_by_token),
) -> NoteDeleteResponse:
    return await delete_existing_note(note_id, user)
