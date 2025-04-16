from app.keys.data.keys_dao import KeysDAO
from app.keys.schemas import key_db_to_key_response, KeysGetResponse
from app.users.data.user_db import UserDB


async def get_all(
        user: UserDB,
) -> KeysGetResponse:
    user_id_filter = {"owner_id": user.item_id}
    keys = await KeysDAO.get_all(**user_id_filter)
    return KeysGetResponse(
        keys=list(map(key_db_to_key_response, keys)),
    )
