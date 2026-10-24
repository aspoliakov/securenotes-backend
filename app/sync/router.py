from fastapi import APIRouter
from fastapi.params import Depends

from app.sync.schemas import SyncResponse
from app.sync.use_cases.sync import get_changes
from app.users.data.session_db import SessionDB
from app.users.data.user_db import UserDB
from app.users.dependencies import get_session_by_token, get_user_by_token

router = APIRouter(prefix='/api/v1/sync', tags=["Sync public route"])


@router.get("", summary="Get User notes and folders changed after the given sync revision")
async def sync(
        since: int | None = None,
        user: UserDB = Depends(get_user_by_token),
        user_session: SessionDB = Depends(get_session_by_token),
) -> SyncResponse:
    return await get_changes(since, user, user_session)
