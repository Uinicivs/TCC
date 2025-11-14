from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from fastapi.exceptions import RequestValidationError

from src.app.core.exceptions import (
    AppException,
    translate_mongo_error,
)


def add_exception_handlers(app: FastAPI) -> None:
    """Adiciona os handlers de exceções na aplicação FastAPI."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
        # Erros de validação de input do FastAPI (body/query/params)
        return JSONResponse(
            status_code=422,
            content={"error": "Request validation error",
                     "details": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # Captura qualquer erro inesperado
        translated = translate_mongo_error(exc)
        return JSONResponse(
            status_code=translated.status_code,
            content={"error": translated.detail},
        )

    @app.exception_handler(RateLimitExceeded)
    async def handle_rate_limit(request: Request, exc: RateLimitExceeded):
        return _rate_limit_exceeded_handler(request, exc)
