from fastapi import APIRouter
from fastapi.params import Depends

from app.users.data.user_db import UserDB
from app.users.dependencies import get_user_by_token
from app.users.schemas import UserRegisterRequest, UserAuthRequest, UserResponse, UserAuthResponse
from app.users.use_cases.auth import user_register, user_authenticate
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
