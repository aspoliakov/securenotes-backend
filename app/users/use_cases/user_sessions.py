from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.users.data.session_db import SessionDB
from app.users.data.sessions_dao import SessionsDAO
from app.users.schemas import (
    UserSessionResponse,
    SessionTerminateResponse,
    OtherSessionsTerminateResponse,
    session_db_to_user_session_response,
)


async def get_user_sessions(current_session: SessionDB) -> list[UserSessionResponse]:
    now = datetime.now(timezone.utc)
    sessions = await SessionsDAO.get_active_by_owner(owner_id=current_session.owner_id, now=now)
    return [session_db_to_user_session_response(session) for session in sessions]


async def terminate_session(current_session: SessionDB, session_id: str) -> SessionTerminateResponse:
    if session_id == current_session.item_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="current session can only be ended by logout",
        )
    deleted = await SessionsDAO.delete_owned(owner_id=current_session.owner_id, item_id=session_id)
    if not deleted:
        # someone else's session is reported the same way as a missing one, so ids can't be probed
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="session not found",
        )
    return SessionTerminateResponse(message="Session terminated")


async def terminate_other_sessions(current_session: SessionDB) -> OtherSessionsTerminateResponse:
    terminated = await SessionsDAO.delete_all_except(
        owner_id=current_session.owner_id,
        item_id=current_session.item_id,
    )
    return OtherSessionsTerminateResponse(message="Other sessions terminated", terminated=terminated)
