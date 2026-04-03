import sqlite3
from collections.abc import Generator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from core.config import Settings, get_settings
from db.repositories import TaskRepository, UserRepository
from db.session import get_db_connection
from services.auth_service import AuthService
from services.task_service import TaskService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="autentificare")


def get_db(settings: Settings = Depends(get_settings)) -> Generator[sqlite3.Connection, None, None]:
    yield from get_db_connection(settings.database_path)


def get_user_repository(db: sqlite3.Connection = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_task_repository(db: sqlite3.Connection = Depends(get_db)) -> TaskRepository:
    return TaskRepository(db)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    settings: Settings = Depends(get_settings),
) -> AuthService:
    return AuthService(user_repository, settings)


def get_task_service(task_repository: TaskRepository = Depends(get_task_repository)) -> TaskService:
    return TaskService(task_repository)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> sqlite3.Row:
    return auth_service.get_current_user(token)
