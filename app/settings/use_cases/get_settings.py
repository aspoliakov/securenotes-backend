from app.settings.data.settings_dao import SettingsDAO
from app.settings.schemas import setting_db_to_setting_response, SettingsGetResponse
from app.users.data.user_db import UserDB


async def get_all(
        user: UserDB,
) -> SettingsGetResponse:
    user_id_filter = {"owner_id": user.item_id}
    settings = await SettingsDAO.get_all(**user_id_filter)
    return SettingsGetResponse(
        settings=list(map(setting_db_to_setting_response, settings)),
    )
