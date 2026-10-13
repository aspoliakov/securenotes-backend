from datetime import datetime

from pydantic import BaseModel, Field

from app.settings.data.setting_db import SettingDB, SETTING_KEY_MAX_LENGTH

MAX_SETTINGS_PER_REQUEST = 50


class SettingResponse(BaseModel):
    key: str = Field(description="setting key")
    value: str = Field(description="setting value")
    updated_at: datetime = Field(description="date of setting update")


class SettingsGetResponse(BaseModel):
    settings: list[SettingResponse] = Field(description="all user's settings")


class SettingPostItem(BaseModel):
    key: str = Field(
        description="setting key, lowercase snake_case",
        pattern=r"^[a-z0-9_]+$",
        min_length=1,
        max_length=SETTING_KEY_MAX_LENGTH,
    )
    value: str = Field(description="setting value, arbitrary string (e.g. serialized json)")


class SettingsPostRequest(BaseModel):
    settings: list[SettingPostItem] = Field(
        description="settings to create or overwrite, other user's settings stay untouched",
        min_length=1,
        max_length=MAX_SETTINGS_PER_REQUEST,
    )


class SettingsPostResponse(BaseModel):
    message: str = Field(description="settings post result message")
    settings: list[SettingResponse] = Field(description="saved user settings")


def setting_db_to_setting_response(setting_db: SettingDB):
    return SettingResponse(
        key=setting_db.key,
        value=setting_db.value,
        updated_at=setting_db.updated_at,
    )
