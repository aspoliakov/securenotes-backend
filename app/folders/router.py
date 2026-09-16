from fastapi import APIRouter
from fastapi.params import Depends

from app.folders.schemas import FolderPostRequest, FoldersGetResponse, FolderPostResponse, FolderDeleteResponse
from app.folders.use_cases.edit_folders import delete_existing_folder, create_or_update_folder
from app.folders.use_cases.get_folders import get_all
from app.users.data.user_db import UserDB
from app.users.dependencies import get_user_by_token

router = APIRouter(prefix='/api/v1/folders', tags=["Folders public route"])


@router.get("/all", summary="Get all User folders")
async def get_all_folders(
        user: UserDB = Depends(get_user_by_token),
) -> FoldersGetResponse:
    return await get_all(user)


@router.post("/save", summary="Create User folder with full JSON")
async def save_folder(
        request: FolderPostRequest,
        user: UserDB = Depends(get_user_by_token),
) -> FolderPostResponse:
    return await create_or_update_folder(request, user)


@router.delete("/{folder_id}", summary="Delete User folder and all its contents by id")
async def delete_folder(
        folder_id: str,
        user: UserDB = Depends(get_user_by_token),
) -> FolderDeleteResponse:
    return await delete_existing_folder(folder_id, user)
