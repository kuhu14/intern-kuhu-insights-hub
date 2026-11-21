from fastapi import FastAPI

from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Read-only API over the cleaned Week 2 secondary sales dataset.",
)
