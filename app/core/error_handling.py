import logging
import sqlite3
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from core.exceptions import AppError

logger = logging.getLogger("app.errors")


def _error_response(
    request: Request,
    status_code: int,
    error_code: str,
    message: str,
    details: list[dict] | None = None,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "-")
    payload: dict = {
        "error": {
            "code": error_code,
            "message": message,
            "status": status_code,
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    }
    if details:
        payload["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=payload)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "application_error code=%s status=%s path=%s request_id=%s message=%s",
            exc.error_code,
            exc.status_code,
            request.url.path,
            getattr(request.state, "request_id", "-"),
            exc.message,
        )
        return _error_response(request, exc.status_code, exc.error_code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.info(
            "validation_error path=%s request_id=%s",
            request.url.path,
            getattr(request.state, "request_id", "-"),
        )
        return _error_response(
            request,
            status_code=422,
            error_code="VALIDATION_ERROR",
            message="Datele trimise nu sunt valide.",
            details=exc.errors(),
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
        message = str(exc.detail) if exc.detail else "Cererea nu a putut fi procesata."
        return _error_response(
            request,
            status_code=exc.status_code,
            error_code="HTTP_ERROR",
            message=message,
        )

    @app.exception_handler(sqlite3.Error)
    async def handle_db_error(request: Request, exc: sqlite3.Error) -> JSONResponse:
        logger.exception(
            "database_error path=%s request_id=%s",
            request.url.path,
            getattr(request.state, "request_id", "-"),
        )
        return _error_response(
            request,
            status_code=503,
            error_code="DATABASE_UNAVAILABLE",
            message="Serviciul de baza de date nu este disponibil momentan.",
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "unexpected_error path=%s request_id=%s",
            request.url.path,
            getattr(request.state, "request_id", "-"),
        )
        return _error_response(
            request,
            status_code=500,
            error_code="INTERNAL_SERVER_ERROR",
            message="A aparut o eroare interna.",
        )
