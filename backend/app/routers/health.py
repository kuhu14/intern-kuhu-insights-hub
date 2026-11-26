from fastapi import APIRouter

from app.schemas.master_data import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health() -> dict[str, str]:
    """Returns {"status": "ok"} when the API is running."""
    return {"status": "ok"}
