from app.data.base_dao import BaseDAO
from app.folders.data.folder_db import FolderDB


class FoldersDAO(BaseDAO):
    model = FolderDB
