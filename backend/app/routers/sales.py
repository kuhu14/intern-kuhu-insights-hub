from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_sales_filters, get_sales_service
from app.repositories.sales_repository import SalesFilters
from app.services.sales_service import SalesService

router = APIRouter(prefix="/sales", tags=["sales"])

ServiceDep = Annotated[SalesService, Depends(get_sales_service)]
FiltersDep = Annotated[SalesFilters, Depends(get_sales_filters)]


@router.get("", summary="List sales rows")
def list_sales(
    service: ServiceDep,
    filters: FiltersDep,
    page: Annotated[int, Query(ge=1, description="Page number, starts at 1")] = 1,
    page_size: Annotated[
        int, Query(ge=1, le=200, description="Rows per page (max 200)")
    ] = 50,
) -> dict[str, Any]:
    """Filtered, paginated sales rows with the total number of matching rows."""
    return service.list_sales(filters, page=page, page_size=page_size)


@router.get("/summary", summary="Summarise sales")
def sales_summary(
    service: ServiceDep,
    filters: FiltersDep,
    group_by: Annotated[
        Literal["region", "state", "brand", "sku", "channel", "month"] | None,
        Query(description="Optional grouping for per-group totals"),
    ] = None,
) -> dict[str, Any]:
    """Total net_value, quantity and row_count, plus groups when group_by is set."""
    return service.summarize(filters, group_by=group_by)
