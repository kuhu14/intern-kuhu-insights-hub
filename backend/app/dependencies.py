from fastapi import Request

from app.repositories.sales_repository import SalesRepository


def get_sales_repository(request: Request) -> SalesRepository:
    """Give routes the repository that was loaded once at startup."""
    return request.app.state.sales_repository
