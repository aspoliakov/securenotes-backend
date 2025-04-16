from app.data.base_dao import BaseDAO
from app.keys.data.key_db import KeyDB


class KeysDAO(BaseDAO):
    model = KeyDB
