from datetime import datetime

from pydantic import AwareDatetime, BaseModel, Field

from app.notes.data.note_db import NoteDB


class NoteResponse(BaseModel):
    note_id: str = Field(description="unique note id")
    folder_id: str | None = Field(description="id of the folder the note belongs to, null if root-level")
    created_at: datetime = Field(description="date of note creation")
    updated_at: datetime = Field(description="date of the last update of the note record (technical)")
    content_updated_at: datetime = Field(description="date of the last note content change")
    key_id: str | None = Field(description="id of the key with which the note is encrypted, null if deleted")
    payload: str | None = Field(description="note encrypted payload, null if deleted")
    order: float = Field(description="sort position within the parent folder")
    deleted_at: datetime | None = Field(description="date of note deletion, null if not deleted")


class NotePostRequest(BaseModel):
    note_id: str = Field(description="unique note id")
    folder_id: str | None = Field(default=None, description="id of the folder the note belongs to, null if root-level")
    key_id: str = Field(description="id of the key with which the note is encrypted")
    payload: str = Field(description="note encrypted payload")
    order: float = Field(description="sort position within the parent folder")
    content_updated_at: AwareDatetime = Field(
        description="the client's content_updated_at: the one it got from the server if the content is unchanged, "
                    "otherwise the local time of the last content change; only compared with the stored one, "
                    "a different value moves content_updated_at to the server time",
    )


class NotePostResponse(BaseModel):
    message: str = Field(description="note post result message")
    note: NoteResponse = Field(description="created user note")


class NoteDeleteResponse(BaseModel):
    message: str = Field(description="note delete result message")


def note_db_to_note_response(note_db: NoteDB):
    return NoteResponse(
        note_id=note_db.item_id,
        folder_id=note_db.folder_id,
        created_at=note_db.created_at,
        updated_at=note_db.updated_at,
        content_updated_at=note_db.content_updated_at,
        key_id=note_db.key_id,
        payload=note_db.payload,
        order=note_db.order,
        deleted_at=note_db.deleted_at,
    )
