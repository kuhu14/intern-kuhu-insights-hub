from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.errors import register_exception_handlers
from app.repositories.sales_repository import SalesRepository
from app.routers import health, master_data, sales


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Load the CSV once at startup; every request reuses this object.
    app.state.sales_repository = SalesRepository(settings.sales_csv_path)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Read-only API over the cleaned Week 2 secondary sales dataset.",
    lifespan=lifespan,
)

register_exception_handlers(app)

app.include_router(health.router)
app.include_router(sales.router)
app.include_router(master_data.router)
