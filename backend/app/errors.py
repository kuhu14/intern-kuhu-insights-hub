import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class NotFoundError(Exception):
    """Raised by services when a requested value does not exist in the data."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    """Build the one error shape: {"error": {"code": ..., "message": ...}}."""
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return error_response(404, exc.code, exc.message)


async def validation_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    messages = []
    for err in exc.errors():
        # loc looks like ("query", "page_size"); drop the "query" part.
        field = ".".join(str(part) for part in err["loc"] if part != "query")
        text = err["msg"].removeprefix("Value error, ")
        messages.append(f"{field}: {text}" if field else text)
    return error_response(422, "VALIDATION_ERROR", "; ".join(messages))


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    codes = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}
    return error_response(
        exc.status_code, codes.get(exc.status_code, "HTTP_ERROR"), str(exc.detail)
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Log the real error for us; never send internal details to the client.
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return error_response(500, "INTERNAL_ERROR", "An unexpected error occurred.")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(NotFoundError, not_found_handler)
    app.add_exception_handler(RequestValidationError, validation_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
