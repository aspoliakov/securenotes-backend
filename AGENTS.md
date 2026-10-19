# AGENTS.md

This file provides guidance to AI coding agents (including Claude Code, claude.ai/code) when working with code in this repository.

## Project

FastAPI backend for the KMP app SecureNotes (https://github.com/aspoliakov/securenotes) — an end-to-end-encrypted notes service. Notes and private keys are stored server-side already encrypted; the server never sees plaintext (`payload`, `encrypted_private_key` are opaque blobs to it).

## Setup & commands

Dependencies are managed with [uv](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock`) targeting Python 3.13.

```bash
uv sync                             # creates .venv and installs pinned dependencies

docker-compose up -d                # starts Postgres on localhost:5433 (user/db: dbadmin/securenotes)

uv run alembic revision --autogenerate -m "message"   # generate a migration after changing models
uv run alembic upgrade head                            # apply migrations

uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000     # dev server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

There is no test suite, linter, or CI config in this repo currently.

A `.env` file in the project root is required (gitignored, not present by default):
```
DB_HOST=...
DB_PORT=...
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
SECRET_KEY=...
ALGORITHM=HS256
GOOGLE_WEB_CLIENT_ID=...
```
Config is loaded via `app/config.py` (`pydantic-settings`); this is the only place env vars are read.

## Architecture

Three vertical feature modules under `app/` — `users`, `notes`, `keys` — each following the same layered structure:

```
app/<feature>/
  router.py              # FastAPI APIRouter, prefix /api/v1/<feature>; thin — only calls use_cases
  schemas.py              # Pydantic request/response models + a `<model>_db_to_<x>_response` mapper
  data/
    <feature>_db.py       # SQLAlchemy ORM model (inherits app.database.Base)
    <feature>s_dao.py      # DAO class (inherits app.data.base_dao.BaseDAO), feature-specific queries
  use_cases/
    *.py                   # business logic; raises fastapi.HTTPException for error cases
```

Routers are wired up in `app/main.py`. Follow this same file layout when adding a new feature module.

**Data layer**: `app/database.py` defines the async SQLAlchemy engine/session (`asyncpg` driver) and the shared `Base` model with common columns every table gets: `id` (int PK), `item_id` (unique string, used as the public-facing ID instead of the numeric PK — always a UUID string set by the use_case, e.g. `str(uuid.uuid4())`), `created_at`, `updated_at`.

`app/data/base_dao.py` (`BaseDAO`) provides generic `get_all`, `get_by_id_or_none` (looked up by `item_id`), `insert`, `update`, `delete`, each opening its own `async_session_maker()` session. Feature DAOs subclass it and only add feature-specific queries (e.g. `UsersDAO.get_by_email`).

**Auth**: access + refresh tokens bound to a server-side session (`app.users.use_cases.sessions`, `SessionDB` in `user_sessions` — one row per signed-in device). Register/authenticate call `create_session`, which returns an `IssuedSession` (the session plus the freshly issued tokens; the plaintext refresh token exists only there, the DB stores its SHA-256 hash).
- Access token: JWT (`PyJWT`, `SECRET_KEY`/`ALGORITHM`), 24 h, standard `exp` plus `sub` (user id) and `sid` (session `item_id`). Sent in the `access_token` header (not `Authorization`) and checked by the `app.users.dependencies.get_user_by_token` dependency: signature/`exp` first, then the session row must still exist, so deleting it revokes the token immediately.
- Refresh token: opaque `secrets.token_urlsafe(32)`, single-use. `POST /api/v1/users/refresh` rotates it and extends the session (sliding 90 days). Replaying a rotated-out token revokes the whole session (theft detection), except within a 30 s grace window meant for a client retrying after a lost response.
- `POST /api/v1/users/logout` takes the refresh token and deletes its session; idempotent (200 for an unknown token).
- Expired sessions of a user are purged when that user gets a new one.

Password hashing (`bcrypt`, used directly — no `passlib`) lives in `app.users.use_cases.auth`. Protected routes take `user: UserDB = Depends(get_user_by_token)`.

**Authorization model**: ownership-based — notes and keys have an `owner_id` FK to `users.item_id`; use_cases check `resource.owner_id == user.item_id` and raise 403 otherwise. `Role` (admin/user) enum on `UserDB` only gates the admin-only "get all users" endpoint.

**Migrations**: Alembic, configured in `app/migration/env.py` to run async (`async_engine_from_config` + `run_sync`), importing `Base` and every model module explicitly so `target_metadata` picks up all tables — new feature models must be imported there too. DB URL comes from `app.database.DATABASE_URL`, not `alembic.ini`.
