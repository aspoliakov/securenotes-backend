from fastapi import HTTPException, status

from app.users.data.user_db import UserDB, Role
from app.users.data.users_dao import UsersDAO
from app.users.schemas import UserResponse, user_db_to_user_response


async def get_all(
        user: UserDB,
) -> list[UserResponse]:
    if user.role == Role.admin:
        users = await UsersDAO.get_all()
        return list(map(user_db_to_user_response, users))
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="access denied",
        )
