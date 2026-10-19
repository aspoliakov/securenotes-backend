from fastapi import APIRouter
from fastapi.params import Depends

from app.users.data.session_db import SessionDB
from app.users.data.user_db import UserDB
from app.users.dependencies import get_user_by_token, get_session_by_token
from app.users.schemas import (
    UserRegisterRequest,
    UserAuthRequest,
    GoogleAuthRequest,
    UserResponse,
    UserAuthResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
    UserLogoutRequest,
    UserLogoutResponse,
    UserSessionResponse,
    SessionTerminateResponse,
    OtherSessionsTerminateResponse,
)
from app.users.use_cases.auth import (
    user_register,
    user_authenticate,
    user_authenticate_google,
    user_refresh_token,
    user_logout,
)
from app.users.use_cases.get_users import get_all
from app.users.use_cases.user_sessions import get_user_sessions, terminate_session, terminate_other_sessions

router = APIRouter(prefix='/api/v1/users', tags=["Users public route"])


@router.post("/", summary="Get all Users")
async def get_all_users(
        user: UserDB = Depends(get_user_by_token),
) -> list[UserResponse]:
    return await get_all(user)


@router.post("/register", summary="Register new User")
async def register(request: UserRegisterRequest) -> UserAuthResponse:
    return await user_register(request)


@router.post("/authenticate", summary="Authenticate User")
async def authenticate(request: UserAuthRequest) -> UserAuthResponse:
    return await user_authenticate(request)


@router.post("/authenticate/google", summary="Authenticate User with Google")
async def authenticate_google(request: GoogleAuthRequest) -> UserAuthResponse:
    return await user_authenticate_google(request)


@router.post("/refresh", summary="Exchange refresh token for a new token pair")
async def refresh(request: TokenRefreshRequest) -> TokenRefreshResponse:
    return await user_refresh_token(request)


@router.post("/logout", summary="Revoke User session")
async def logout(request: UserLogoutRequest) -> UserLogoutResponse:
    return await user_logout(request)


@router.get("/sessions", summary="Get active sessions of the User")
async def get_sessions(
        session: SessionDB = Depends(get_session_by_token),
) -> list[UserSessionResponse]:
    return await get_user_sessions(session)


@router.delete("/sessions", summary="Terminate all User sessions except the current one")
async def delete_other_sessions(
        session: SessionDB = Depends(get_session_by_token),
) -> OtherSessionsTerminateResponse:
    return await terminate_other_sessions(session)


@router.delete("/sessions/{session_id}", summary="Terminate a User session other than the current one")
async def delete_session(
        session_id: str,
        session: SessionDB = Depends(get_session_by_token),
) -> SessionTerminateResponse:
    return await terminate_session(session, session_id)
