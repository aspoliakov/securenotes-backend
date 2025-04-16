from datetime import datetime, timezone

from fastapi import HTTPException, status, Depends, Header
from jose import jwt, JWTError

from app.config import get_auth_data
from app.users.data.user_db import UserDB
from app.users.data.users_dao import UsersDAO


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
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(
            token=token,
            key=auth_data['secret_key'],
            algorithms=[auth_data['algorithm']],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="access_token is not valid",
        )

    expires_at = payload.get("expires_at")
    expire_time = datetime.fromisoformat(expires_at)
    if (not expires_at) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="access_token expired",
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user_id not found",
        )

    user = await UsersDAO.get_by_id_or_none(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user not found",
        )

    return user
