from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Health check")
def health() -> dict[str, str]:
    """Returns {"status": "ok"} when the API is running."""
    return {"status": "ok"}
