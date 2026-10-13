from fastapi import APIRouter
from fastapi.params import Depends

from app.settings.schemas import SettingsGetResponse, SettingsPostRequest, SettingsPostResponse
from app.settings.use_cases.edit_settings import save_settings
from app.settings.use_cases.get_settings import get_all
from app.users.data.user_db import UserDB
from app.users.dependencies import get_user_by_token

router = APIRouter(prefix='/api/v1/settings', tags=["Settings public route"])


@router.get("/all", summary="Get all User settings")
async def get_all_settings(
        user: UserDB = Depends(get_user_by_token),
) -> SettingsGetResponse:
    return await get_all(user)


@router.post("/save", summary="Create or overwrite User settings by key")
async def save_user_settings(
        request: SettingsPostRequest,
        user: UserDB = Depends(get_user_by_token),
) -> SettingsPostResponse:
    return await save_settings(request, user)
