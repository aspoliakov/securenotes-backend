from fastapi import APIRouter
from fastapi.params import Depends

from app.users.data.user_db import UserDB
from app.users.dependencies import get_user_by_token
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
)
from app.users.use_cases.auth import (
    user_register,
    user_authenticate,
    user_authenticate_google,
    user_refresh_token,
    user_logout,
)
from app.users.use_cases.get_users import get_all

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
