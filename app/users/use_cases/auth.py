import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext

from app.config import get_auth_data
from app.users.data.user_db import UserDB
from app.users.data.users_dao import UsersDAO
from app.users.schemas import UserRegisterRequest, UserAuthRequest, UserAuthResponse, user_db_to_user_response

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def user_register(request: UserRegisterRequest) -> UserAuthResponse:
    user = await UsersDAO.get_by_email(email=request.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user already registererd",
        )
    user_db_dict = {
        "email": request.email,
        "password": get_password_hash(request.password),
        "item_id": str(uuid.uuid4()),
        "avatar": None,
    }
    user_db: UserDB = await UsersDAO.insert(**user_db_dict)
    if user_db:
        access_token = create_access_token_with_user_id(user_db.item_id)
        return UserAuthResponse(
            message="User registered",
            user=user_db_to_user_response(user_db),
            token=access_token,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def user_authenticate(request: UserAuthRequest) -> UserAuthResponse:
    user_db = await UsersDAO.get_by_email(email=request.email)
    if not user_db or verify_password(plain_password=request.password, hashed_password=user_db.password) is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="wrong credentials",
        )
    access_token = create_access_token_with_user_id(user_db.item_id)
    return UserAuthResponse(
        message="User registered",
        user=user_db_to_user_response(user_db),
        token=access_token,
    )


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token_with_user_id(user_id: str) -> str:
    return create_access_token(
        {
            "user_id": user_id,
        }
    )


def create_access_token(data: dict) -> str:
    jwt_data = data.copy()
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    jwt_data.update({"expires_at": expires_at.isoformat()})
    auth_data = get_auth_data()
    encode_jwt = jwt.encode(
        claims=jwt_data,
        key=auth_data['secret_key'],
        algorithm=auth_data['algorithm'],
    )
    return encode_jwt
