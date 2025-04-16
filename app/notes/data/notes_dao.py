from app.data.base_dao import BaseDAO
from app.notes.data.note_db import NoteDB


class NotesDAO(BaseDAO):
    model = NoteDB
