from fastapi import APIRouter
from fastapi.params import Depends

from app.keys.schemas import KeyResponse, KeyPostRequest, KeyPostResponse, KeyDeleteResponse, KeysGetResponse
from app.keys.use_cases.edit_keys import create_new_key, delete_old_key
from app.keys.use_cases.get_keys import get_all
from app.users.data.user_db import UserDB
from app.users.dependencies import get_user_by_token

router = APIRouter(prefix='/api/v1/keys', tags=["Keys public route"])


@router.get("/all", summary="Get all user keys")
async def get_all_keys(
        user: UserDB = Depends(get_user_by_token),
) -> KeysGetResponse:
    return await get_all(user)


@router.post("/new", summary="Create new key by user")
async def create_key(
        request: KeyPostRequest,
        user: UserDB = Depends(get_user_by_token),
) -> KeyPostResponse:
    return await create_new_key(request, user)


@router.delete("/{key_id}", summary="Delete user key by id")
async def delete_key(
        key_id: str,
        user: UserDB = Depends(get_user_by_token),
) -> KeyDeleteResponse:
    return await delete_old_key(key_id, user)
