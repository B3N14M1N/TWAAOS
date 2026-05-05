from contextlib import asynccontextmanager
from pathlib import Path
from typing import Iterable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
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
    web_dir = base_dir / "web"

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5500",
            "http://127.0.0.1:5500",
            "null",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RequestContextMiddleware)
    register_exception_handlers(app)

    app.include_router(auth_router)
    app.include_router(tasks_router)

    if web_dir.exists():
        @app.middleware("http")
        async def web_no_cache_headers(request, call_next):
            response = await call_next(request)
            if request.url.path.startswith("/web"):
                response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"
            return response

        @app.get("/web/version", include_in_schema=False)
        def web_version() -> dict[str, str]:
            return {"version": _current_web_version(web_dir)}

        app.mount("/web", StaticFiles(directory=str(web_dir), html=True), name="web")

        @app.get("/", include_in_schema=False)
        def root_redirect() -> RedirectResponse:
            return RedirectResponse(url="/web/index.html")

    return app
