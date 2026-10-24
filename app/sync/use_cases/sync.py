from datetime import datetime, timezone

from app.database import async_session_maker
from app.folders.data.folder_db import FolderDB
from app.folders.schemas import folder_db_to_folder_response
from app.notes.data.note_db import NoteDB
from app.notes.schemas import note_db_to_note_response
from app.sync.data.sync_dao import SyncDAO
from app.sync.schemas import SyncResponse
from app.users.data.session_db import SessionDB
from app.users.data.user_db import UserDB


async def get_changes(
        since: int | None,
        user: UserDB,
        user_session: SessionDB,
) -> SyncResponse:
    async with async_session_maker() as session:
        async with session.begin():
            # the revision first: rows read after it may only be newer, never missing
            revision = await SyncDAO.get_revision(session, user.item_id)
            if since is not None and since > revision:
                # a cursor of another database state (e.g. a recreated one): start over as a first sync
                since = None
            notes = await SyncDAO.get_changed(session, NoteDB, user.item_id, since)
            folders = await SyncDAO.get_changed(session, FolderDB, user.item_id, since)
    await _forget_synced_tombstones(user, user_session, revision if since is None else since)
    return SyncResponse(
        sync_revision=revision,
        notes=list(map(note_db_to_note_response, notes)),
        folders=list(map(folder_db_to_folder_response, folders)),
    )


async def _forget_synced_tombstones(user: UserDB, user_session: SessionDB, applied_revision: int) -> None:
    """
    A device sends as since the revision it has applied, so tombstones up to the oldest such revision of
    the user's active devices are no longer needed. A first sync gets no tombstones at all, so for it the
    returned revision counts: if the device loses the response, it starts over as a first sync again.
    """
    async with async_session_maker() as session:
        async with session.begin():
            await SyncDAO.save_session_revision(session, user_session.item_id, applied_revision)
            min_revision = await SyncDAO.get_min_session_revision(session, user.item_id, datetime.now(timezone.utc))
            if min_revision is not None:
                await SyncDAO.delete_tombstones(session, user.item_id, min_revision)
