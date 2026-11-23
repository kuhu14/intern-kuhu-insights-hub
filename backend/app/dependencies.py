from typing import Annotated

from fastapi import Depends, Request

from app.repositories.sales_repository import SalesRepository
from app.services.sales_service import SalesService


def get_sales_repository(request: Request) -> SalesRepository:
    """Give routes the repository that was loaded once at startup."""
    return request.app.state.sales_repository


def get_sales_service(
    repository: Annotated[SalesRepository, Depends(get_sales_repository)],
) -> SalesService:
    return SalesService(repository)
