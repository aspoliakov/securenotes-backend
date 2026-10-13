import uuid

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError

from app.data.base_dao import BaseDAO
from app.database import async_session_maker
from app.settings.data.setting_db import SettingDB


class SettingsDAO(BaseDAO):
    model = SettingDB

    @classmethod
    async def count_keys_excluding(cls, owner_id: str, keys: list[str]) -> int:
        async with async_session_maker() as session:
            query = (
                select(func.count())
                .select_from(SettingDB)
                .where(SettingDB.owner_id == owner_id, SettingDB.key.not_in(keys))
            )
            result = await session.execute(query)
            return result.scalar_one()

    @classmethod
    async def upsert_many(cls, owner_id: str, values_by_key: dict[str, str]) -> list[SettingDB]:
        """Insert or overwrite every (owner_id, key) pair in one statement."""
        async with async_session_maker() as session:
            async with session.begin():
                insert_query = pg_insert(SettingDB).values([
                    {
                        "item_id": str(uuid.uuid4()),
                        "owner_id": owner_id,
                        "key": key,
                        "value": value,
                    }
                    for key, value in values_by_key.items()
                ])
                upsert_query = insert_query.on_conflict_do_update(
                    constraint="uq_user_settings_owner_id_key",
                    set_={
                        "value": insert_query.excluded.value,
                        "updated_at": func.now(),
                    },
                ).returning(SettingDB)
                try:
                    result = await session.execute(upsert_query)
                    settings = list(result.scalars().all())
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return settings
