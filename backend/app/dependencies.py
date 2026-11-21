from datetime import date
from typing import Annotated

from fastapi import Depends, Query, Request

from app.repositories.sales_repository import SalesFilters, SalesRepository
from app.services.sales_service import SalesService


def get_sales_repository(request: Request) -> SalesRepository:
    """Give routes the repository that was loaded once at startup."""
    return request.app.state.sales_repository


def get_sales_service(
    repository: Annotated[SalesRepository, Depends(get_sales_repository)],
) -> SalesService:
    return SalesService(repository)


def get_sales_filters(
    region: Annotated[str | None, Query(description="Region, e.g. North")] = None,
    state: Annotated[str | None, Query(description="State, e.g. Bihar")] = None,
    brand: Annotated[str | None, Query(description="Brand, e.g. Navratna")] = None,
    sku_code: Annotated[str | None, Query(description="SKU code, e.g. EM-1003")] = None,
    channel: Annotated[
        str | None, Query(description="Channel, e.g. General Trade")
    ] = None,
    date_from: Annotated[
        date | None, Query(description="Start date (YYYY-MM-DD), inclusive")
    ] = None,
    date_to: Annotated[
        date | None, Query(description="End date (YYYY-MM-DD), inclusive")
    ] = None,
    is_return: Annotated[
        bool | None, Query(description="true = only returns, false = only sales")
    ] = None,
) -> SalesFilters:
    """Read the shared filter query parameters into one SalesFilters object."""
    return SalesFilters(
        region=region,
        state=state,
        brand=brand,
        sku_code=sku_code,
        channel=channel,
        date_from=date_from,
        date_to=date_to,
        is_return=is_return,
    )
