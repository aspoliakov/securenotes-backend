from pydantic import BaseModel, Field

from app.folders.schemas import FolderResponse
from app.notes.schemas import NoteResponse


class SyncResponse(BaseModel):
    sync_revision: int = Field(
        description="revision of the user's data the response is up to: pass it back as since on the next sync, "
                    "unchanged data returns the same one",
    )
    notes: list[NoteResponse] = Field(
        description="notes changed after since, deleted ones (deleted_at is set) included; "
                    "all existing notes without since",
    )
    folders: list[FolderResponse] = Field(
        description="folders changed after since, deleted ones (deleted_at is set) included; "
                    "all existing folders without since",
    )
