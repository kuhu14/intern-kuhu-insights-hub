from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.errors import register_exception_handlers
from app.repositories.factory import build_sales_repository
from app.routers import health, master_data, sales

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Build the repository once at startup (REPOSITORY=file or postgres);
    # every request reuses this object.
    app.state.sales_repository = build_sales_repository(settings)
    yield

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Read-only API over the cleaned Week 2 secondary sales dataset.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)


register_exception_handlers(app)

app.include_router(health.router)
app.include_router(sales.router)
app.include_router(master_data.router)
