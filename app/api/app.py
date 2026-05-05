from contextlib import asynccontextmanager
from pathlib import Path
from typing import Iterable

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

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


def _iter_web_files(web_dir: Path) -> Iterable[Path]:
    for pattern in ("*.html", "*.css", "*.js"):
        yield from web_dir.rglob(pattern)


def _current_web_version(web_dir: Path) -> str:
    timestamps = [str(file.stat().st_mtime_ns) for file in _iter_web_files(web_dir)]
    if not timestamps:
        return "0"
    return str(max(timestamps))


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    base_dir = Path(__file__).resolve().parent.parent
    static_dir = base_dir / "static"

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(RequestContextMiddleware)
    register_exception_handlers(app)

    app.include_router(auth_router)
    app.include_router(tasks_router)

    @app.get("/healthz", include_in_schema=False)
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    if static_dir.exists():
        @app.middleware("http")
        async def web_no_cache_headers(request, call_next):
            response = await call_next(request)
            if request.url.path.startswith("/assets") or request.url.path in ("/", "/index.html"):
                response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"
            return response

        @app.get("/version", include_in_schema=False)
        def web_version() -> dict[str, str]:
            return {"version": _current_web_version(static_dir)}

        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app
