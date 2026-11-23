from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(description="Machine-readable error code, e.g. VALIDATION_ERROR")
    message: str = Field(description="Human-readable explanation of what went wrong")


class ErrorResponse(BaseModel):
    """The single error shape every endpoint uses."""

    error: ErrorDetail


# Reuse on routers so /docs shows the real error shape for these status codes.
ERROR_RESPONSES: dict[int | str, dict] = {
    404: {"model": ErrorResponse, "description": "Not found"},
    422: {"model": ErrorResponse, "description": "Invalid input"},
}
