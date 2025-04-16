from datetime import datetime

from pydantic import BaseModel, Field, EmailStr

from app.users.data.user_db import UserDB, Role


class UserResponse(BaseModel):
    user_id: str = Field(description="user id")
    created_at: datetime = Field(description="date of user creation")
    updated_at: datetime = Field(description="date of user update")
    email: str | None = Field(description="user email")
    login: str | None = Field(description="user login")
    role: Role | None = Field(description="user role")
    avatar: str | None = Field(description="user avatar")


class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(description="user email")
    password: str = Field(description="user password")


class UserAuthRequest(BaseModel):
    email: EmailStr = Field(description="user email")
    password: str = Field(description="user password")


class UserAuthResponse(BaseModel):
    message: str = Field(description="auth result message")
    user: UserResponse = Field(description="user data")
    token: str = Field(description="user access token")


def user_db_to_user_response(user: UserDB):
    return UserResponse(
        user_id=user.item_id,
        created_at=user.created_at,
        updated_at=user.updated_at,
        email=user.email,
        login=user.login,
        role=user.role,
        avatar=user.avatar,
    )
