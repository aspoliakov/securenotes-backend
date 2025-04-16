from datetime import datetime

from pydantic import BaseModel, Field

from app.keys.data.key_db import KeyDB


class KeyResponse(BaseModel):
    key_id: str = Field(description="unique key id")
    created_at: datetime = Field(description="date of key creation")
    updated_at: datetime = Field(description="date of key update")
    public_key: str = Field(description="public part of the key")
    encrypted_private_key: str = Field(description="encrypted private part of the key")
    version: int = Field(description="version of the key")


class KeysGetResponse(BaseModel):
    keys: list[KeyResponse] = Field(description="all user's keys")


class KeyPostRequest(BaseModel):
    public_key: str = Field(description="public part of the key")
    encrypted_private_key: str = Field(description="encrypted private part of the key")


class KeyPostResponse(BaseModel):
    message: str = Field(description="key post result message")
    key: KeyResponse = Field(description="created user key")


class KeyDeleteResponse(BaseModel):
    message: str = Field(description="success message")


def key_db_to_key_response(key_db: KeyDB):
    return KeyResponse(
        key_id=key_db.item_id,
        created_at=key_db.created_at,
        updated_at=key_db.updated_at,
        public_key=key_db.public_key,
        encrypted_private_key=key_db.encrypted_private_key,
        version=key_db.version,
    )
