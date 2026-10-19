from datetime import datetime, timezone

from pydantic import BaseModel, Field, EmailStr

from app.users.data.session_db import SessionDB
from app.users.data.user_db import UserDB, Role


class UserResponse(BaseModel):
    user_id: str = Field(description="user id")
    created_at: datetime = Field(description="date of user creation")
    updated_at: datetime = Field(description="date of user update")
    email: str | None = Field(description="user email")
    login: str | None = Field(description="user login")
    role: Role | None = Field(description="user role")
    avatar: str | None = Field(description="user avatar")


class DeviceInfo(BaseModel):
    device_name: str | None = Field(default=None, description="human-readable device name, e.g. Google Pixel 8")
    platform: str | None = Field(default=None, description="client platform, e.g. android or ios")
    os_version: str | None = Field(default=None, description="platform OS version")


class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(description="user email")
    password: str = Field(description="user password")
    device: DeviceInfo | None = Field(default=None, description="device the session is opened on")


class UserAuthRequest(BaseModel):
    email: EmailStr = Field(description="user email")
    password: str = Field(description="user password")
    device: DeviceInfo | None = Field(default=None, description="device the session is opened on")


class GoogleAuthRequest(BaseModel):
    id_token: str = Field(description="Google ID token from Credential Manager")
    device: DeviceInfo | None = Field(default=None, description="device the session is opened on")


class UserAuthResponse(BaseModel):
    message: str = Field(description="auth result message")
    user: UserResponse = Field(description="user data")
    token: str = Field(description="user access token")
    refresh_token: str = Field(description="single-use token to get a new access token")
    session_id: str = Field(description="id of the session the tokens belong to")


class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(description="current refresh token")


class TokenRefreshResponse(BaseModel):
    message: str = Field(description="refresh result message")
    token: str = Field(description="new user access token")
    refresh_token: str = Field(description="new refresh token, the sent one is no longer valid")


class UserLogoutRequest(BaseModel):
    refresh_token: str = Field(description="refresh token of the session to revoke")


class UserLogoutResponse(BaseModel):
    message: str = Field(description="logout result message")


class UserSessionResponse(BaseModel):
    session_id: str = Field(description="session id")
    created_at: datetime = Field(description="date of sign-in")
    last_active_at: datetime = Field(description="date of the last token refresh, sign-in date if none yet")
    expires_at: datetime = Field(description="date the session expires unless refreshed")
    device_name: str | None = Field(description="device name reported at sign-in")
    platform: str | None = Field(description="client platform reported at sign-in")
    os_version: str | None = Field(description="OS version reported at sign-in")


class SessionTerminateResponse(BaseModel):
    message: str = Field(description="termination result message")


class OtherSessionsTerminateResponse(BaseModel):
    message: str = Field(description="termination result message")
    terminated: int = Field(description="number of terminated sessions")


def session_db_to_user_session_response(session: SessionDB):
    created_at = as_utc(session.created_at)
    return UserSessionResponse(
        session_id=session.item_id,
        created_at=created_at,
        last_active_at=session.rotated_at or created_at,
        expires_at=session.expires_at,
        device_name=session.device_name,
        platform=session.platform,
        os_version=session.os_version,
    )


def as_utc(value: datetime) -> datetime:
    # created_at is a naive column filled by the DB's now(), which runs in UTC
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


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
