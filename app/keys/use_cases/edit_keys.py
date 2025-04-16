import uuid

from fastapi import HTTPException, status

from app.keys.data.key_db import KeyDB
from app.keys.data.keys_dao import KeysDAO
from app.keys.schemas import KeyPostRequest, KeyPostResponse, key_db_to_key_response, KeyDeleteResponse
from app.users.data.user_db import UserDB


async def create_new_key(
        request: KeyPostRequest,
        user: UserDB,
) -> KeyPostResponse:
    key_db_dict = {
        "item_id": str(uuid.uuid4()),
        "owner_id": user.item_id,
        "public_key": request.public_key,
        "encrypted_private_key": request.encrypted_private_key,
        "version": 0,  # TODO: increment version by current latest user key
    }
    key_db: KeyDB = await KeysDAO.insert(**key_db_dict)
    if key_db:
        return KeyPostResponse(
            message="key created",
            key=key_db_to_key_response(key_db),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def delete_old_key(
        key_id: str,
        user: UserDB,
) -> KeyDeleteResponse:
    key: KeyDB = await KeysDAO.get_by_id_or_none(key_id)
    if key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    elif key.owner_id != user.item_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="access denied",
        )
    else:
        check = await KeysDAO.delete(item_id=key_id)
        if check:
            return KeyDeleteResponse(
                message=f"key with id {key_id} deleted",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
