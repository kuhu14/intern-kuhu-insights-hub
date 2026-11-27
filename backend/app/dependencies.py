from typing import Annotated

from fastapi import Depends, Request

from app.repositories.protocol import SalesRepositoryProtocol
from app.services.sales_service import SalesService


def get_sales_repository(request: Request) -> SalesRepositoryProtocol:
    """Give routes the repository that was built once at startup."""
    return request.app.state.sales_repository


def get_sales_service(
    repository: Annotated[SalesRepositoryProtocol, Depends(get_sales_repository)],
) -> SalesService:
    return SalesService(repository)
