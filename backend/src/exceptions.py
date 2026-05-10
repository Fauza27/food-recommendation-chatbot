"""Custom exceptions dan error handlers untuk Food Recommendation API."""

from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base exception untuk application-level errors."""

    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ServiceUnavailableError(AppError):
    """Dilempar ketika service eksternal tidak tersedia."""

    def __init__(self, service: str, detail: str = "") -> None:
        super().__init__(
            code="SERVICE_UNAVAILABLE",
            message=f"{service} tidak tersedia. {detail}".strip(),
            status_code=503,
        )


class RateLimitError(AppError):
    """Dilempar ketika rate limit terlampaui."""

    def __init__(self) -> None:
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message="Terlalu banyak permintaan. Coba lagi dalam beberapa saat.",
            status_code=429,
        )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handler untuk semua AppError — mengembalikan format error konsisten."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": getattr(request.state, "request_id", "unknown"),
            }
        },
    )
