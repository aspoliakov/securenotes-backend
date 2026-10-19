from fastapi import HTTPException, status, Depends, Header

from app.users.data.user_db import UserDB
from app.users.data.users_dao import UsersDAO
from app.users.use_cases.sessions import get_active_session


class TokenChecker:
    def __call__(self, access_token: str = Header(..., alias="access_token")):
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="access_token is required",
            )
        return access_token


token_checker = TokenChecker()


async def get_user_by_token(token: str = Depends(token_checker)) -> UserDB:
    session = await get_active_session(token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="access_token is not valid",
        )

    user = await UsersDAO.get_by_id_or_none(session.owner_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user not found",
        )

    return user
