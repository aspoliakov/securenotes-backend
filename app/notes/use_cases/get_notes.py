from app.notes.data.notes_dao import NotesDAO
from app.notes.schemas import note_db_to_note_response, NotesGetResponse
from app.users.data.user_db import UserDB


async def get_all(
        user: UserDB,
) -> NotesGetResponse:
    user_id_filter = {"owner_id": user.item_id}
    notes = await NotesDAO.get_all(**user_id_filter)
    return NotesGetResponse(
        notes=list(map(note_db_to_note_response, notes)),
    )
