from app.folders.data.folders_dao import FoldersDAO
from app.folders.schemas import folder_db_to_folder_response, FoldersGetResponse
from app.users.data.user_db import UserDB


async def get_all(
        user: UserDB,
) -> FoldersGetResponse:
    user_id_filter = {"owner_id": user.item_id}
    folders = await FoldersDAO.get_all(**user_id_filter)
    return FoldersGetResponse(
        folders=list(map(folder_db_to_folder_response, folders)),
    )
