from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.middleware import RequestContextMiddleware
from api.routers.auth import router as auth_router
from api.routers.tasks import router as tasks_router
from core.config import get_settings
from core.error_handling import register_exception_handlers
from core.logging_config import configure_logging
from db.schema import initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    initialize_database(settings.database_path)
    yield


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(RequestContextMiddleware)
    register_exception_handlers(app)

    app.include_router(auth_router)
    app.include_router(tasks_router)

    return app
