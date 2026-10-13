from fastapi import HTTPException, status

from app.settings.data.settings_dao import SettingsDAO
from app.settings.schemas import (
    SettingsPostRequest,
    SettingsPostResponse,
    setting_db_to_setting_response,
)
from app.users.data.user_db import UserDB

MAX_SETTINGS_PER_USER = 100


async def save_settings(
        request: SettingsPostRequest,
        user: UserDB,
) -> SettingsPostResponse:
    # duplicate keys within one request: the last one wins
    values_by_key = {item.key: item.value for item in request.settings}

    other_keys_count = await SettingsDAO.count_keys_excluding(user.item_id, list(values_by_key.keys()))
    if other_keys_count + len(values_by_key) > MAX_SETTINGS_PER_USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="settings limit exceeded",
        )

    settings = await SettingsDAO.upsert_many(user.item_id, values_by_key)
    return SettingsPostResponse(
        message="settings saved",
        settings=list(map(setting_db_to_setting_response, settings)),
    )
