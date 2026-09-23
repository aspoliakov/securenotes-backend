import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.config import get_auth_data, get_google_client_id
from app.users.data.user_db import UserDB
from app.users.data.users_dao import UsersDAO
from app.users.schemas import (
    UserRegisterRequest,
    UserAuthRequest,
    UserAuthResponse,
    GoogleAuthRequest,
    user_db_to_user_response,
)


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


async def user_authenticate_google(request: GoogleAuthRequest) -> UserAuthResponse:
    try:
        idinfo = google_id_token.verify_oauth2_token(
            request.id_token,
            google_requests.Request(),
            audience=get_google_client_id(),
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid google token",
        )

    if not idinfo.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="google email not verified",
        )

    provider_id = idinfo["sub"]
    user_db = await UsersDAO.get_by_provider_id(provider="google", provider_id=provider_id)
    if not user_db:
        existing_by_email = await UsersDAO.get_by_email(email=idinfo["email"])
        if existing_by_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="email already registered with password",
            )
        user_db_dict = {
            "email": idinfo["email"],
            "password": None,
            "item_id": str(uuid.uuid4()),
            "avatar": None,
            "provider": "google",
            "provider_id": provider_id,
        }
        user_db = await UsersDAO.insert(**user_db_dict)

    access_token = create_access_token_with_user_id(user_db.item_id)
    return UserAuthResponse(
        message="User registered",
        user=user_db_to_user_response(user_db),
        token=access_token,
    )


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


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
        payload=jwt_data,
        key=auth_data['secret_key'],
        algorithm=auth_data['algorithm'],
    )
    return encode_jwt
