from fastapi import FastAPI

from app.folders.router import router as folders_router
from app.keys.router import router as keys_router
from app.notes.router import router as notes_router
from app.settings.router import router as settings_router
from app.sync.router import router as sync_router
from app.users.router import router as users_router

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(users_router)
app.include_router(notes_router)
app.include_router(keys_router)
app.include_router(folders_router)
app.include_router(settings_router)
app.include_router(sync_router)
