from datetime import datetime

from pydantic import BaseModel, Field

from app.folders.data.folder_db import FolderDB


class FolderResponse(BaseModel):
    folder_id: str = Field(description="unique folder id")
    parent_id: str | None = Field(description="id of the parent folder, null if root-level")
    created_at: datetime = Field(description="date of folder creation")
    updated_at: datetime = Field(description="date of folder update")
    key_id: str = Field(description="id of the key with which the folder is encrypted")
    payload: str = Field(description="folder encrypted payload")
    order: float = Field(description="sort position within the parent folder")


class FoldersGetResponse(BaseModel):
    folders: list[FolderResponse] = Field(description="all user's folders")


class FolderPostRequest(BaseModel):
    folder_id: str = Field(description="unique folder id")
    parent_id: str | None = Field(default=None, description="id of the parent folder, null if root-level")
    key_id: str = Field(description="id of the key with which the folder is encrypted")
    payload: str = Field(description="folder encrypted payload")
    order: float = Field(description="sort position within the parent folder")


class FolderPostResponse(BaseModel):
    message: str = Field(description="folder post result message")
    folder: FolderResponse = Field(description="created user folder")


class FolderDeleteResponse(BaseModel):
    message: str = Field(description="folder delete result message")


def folder_db_to_folder_response(folder_db: FolderDB):
    return FolderResponse(
        folder_id=folder_db.item_id,
        parent_id=folder_db.parent_id,
        created_at=folder_db.created_at,
        updated_at=folder_db.updated_at,
        key_id=folder_db.key_id,
        payload=folder_db.payload,
        order=folder_db.order,
    )
