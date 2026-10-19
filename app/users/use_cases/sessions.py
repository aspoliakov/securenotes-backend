import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import jwt

from app.config import get_auth_data
from app.users.data.session_db import SessionDB
from app.users.data.sessions_dao import SessionsDAO

ACCESS_TOKEN_LIFETIME = timedelta(hours=24)

SESSION_LIFETIME = timedelta(days=90)

REFRESH_TOKEN_REUSE_GRACE = timedelta(seconds=30)

REFRESH_TOKEN_BYTES = 32


@dataclass(frozen=True)
class IssuedSession:
    session: SessionDB
    access_token: str
    # plaintext exists only at issue time: the DB keeps just its hash
    refresh_token: str


async def create_session(user_id: str) -> IssuedSession:
    now = datetime.now(timezone.utc)
    await SessionsDAO.delete_expired(owner_id=user_id, now=now)
    refresh_token = generate_refresh_token()
    session = await SessionsDAO.insert(
        item_id=str(uuid.uuid4()),
        owner_id=user_id,
        refresh_token_hash=hash_token(refresh_token),
        expires_at=now + SESSION_LIFETIME,
    )
    return IssuedSession(
        session=session,
        access_token=create_access_token(session),
        refresh_token=refresh_token,
    )


async def refresh_session(refresh_token: str) -> IssuedSession | None:
    """Rotates the refresh token. None means the session is gone and the client has to sign in again."""
    now = datetime.now(timezone.utc)
    token_hash = hash_token(refresh_token)
    rotated_at = now
    session = await SessionsDAO.get_by_refresh_token_hash(token_hash)
    if not session:
        session = await SessionsDAO.get_by_previous_refresh_token_hash(token_hash)
        if not session:
            return None
        if session.rotated_at is None or now - session.rotated_at > REFRESH_TOKEN_REUSE_GRACE:
            # a rotated-out token is replayed: someone else holds a copy, so neither copy can be trusted
            await SessionsDAO.delete(item_id=session.item_id)
            return None
        # retry within the grace window: keep the original rotation time so the window doesn't slide
        rotated_at = session.rotated_at

    if session.expires_at < now:
        await SessionsDAO.delete(item_id=session.item_id)
        return None

    new_refresh_token = generate_refresh_token()
    updated = await SessionsDAO.update(
        # compare-and-set: a concurrent refresh with the same token must not rotate twice
        filter_by={"item_id": session.item_id, "refresh_token_hash": session.refresh_token_hash},
        refresh_token_hash=hash_token(new_refresh_token),
        previous_refresh_token_hash=token_hash,
        rotated_at=rotated_at,
        expires_at=now + SESSION_LIFETIME,
    )
    if not updated:
        return None

    session = await SessionsDAO.get_by_id_or_none(session.item_id)
    return IssuedSession(
        session=session,
        access_token=create_access_token(session),
        refresh_token=new_refresh_token,
    )


async def revoke_session(refresh_token: str):
    await SessionsDAO.delete_by_refresh_token_hash(hash_token(refresh_token))


async def get_active_session(access_token: str) -> SessionDB | None:
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(
            jwt=access_token,
            key=auth_data['secret_key'],
            algorithms=[auth_data['algorithm']],
            options={"require": ["exp", "sub", "sid"]},
        )
    except jwt.PyJWTError:
        return None

    session = await SessionsDAO.get_by_id_or_none(payload["sid"])
    if not session or session.owner_id != payload["sub"] or session.expires_at < datetime.now(timezone.utc):
        return None
    return session


def create_access_token(session: SessionDB) -> str:
    now = datetime.now(timezone.utc)
    auth_data = get_auth_data()
    return jwt.encode(
        payload={
            "sub": session.owner_id,
            "sid": session.item_id,
            "iat": now,
            "exp": now + ACCESS_TOKEN_LIFETIME,
        },
        key=auth_data['secret_key'],
        algorithm=auth_data['algorithm'],
    )


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(REFRESH_TOKEN_BYTES)


def hash_token(token: str) -> str:
    # a plain fast hash is enough here: the token is random and high-entropy, unlike a password
    return hashlib.sha256(token.encode()).hexdigest()
