# SecureNotes Backend

Backend for the KMP App [SecureNotes](https://github.com/aspoliakov/securenotes)

# Setup

Dependencies are managed with [uv](https://docs.astral.sh/uv/). Install all dependencies (creates `.venv` targeting Python 3.13):

> uv sync

Setup PostgreSQL config. Create a file ".env" in the root directory with the following contents (**replace values**):

```
DB_HOST='host_ip'
DB_PORT=5433
DB_NAME='db_name'
DB_USER='db_super_user'
DB_PASSWORD='db_pass'
SECRET_KEY='jwt_secret_key'
ALGORITHM='HS256'
```

Run PostgreSQL in Docker (first install docker-compose):

> docker-compose up -d

Apply migrations:

> uv run alembic upgrade head

Run app in dev environment:

> uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000

Run app via uvicorn:

> uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
