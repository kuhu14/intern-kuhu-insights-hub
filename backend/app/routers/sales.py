from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_sales_service
from app.schemas.sales import (
    SalesListParams,
    SalesPage,
    SalesSummary,
    SalesSummaryParams,
)
from app.services.sales_service import SalesService

router = APIRouter(prefix="/sales", tags=["sales"])

ServiceDep = Annotated[SalesService, Depends(get_sales_service)]


@router.get("", response_model=SalesPage, summary="List sales rows")
def list_sales(
    service: ServiceDep, params: Annotated[SalesListParams, Query()]
) -> dict[str, Any]:
    """Filtered, paginated sales rows with the total number of matching rows."""
    return service.list_sales(params)


@router.get(
    "/summary",
    response_model=SalesSummary,
    response_model_exclude_none=True,
    summary="Summarise sales",
)
def sales_summary(
    service: ServiceDep, params: Annotated[SalesSummaryParams, Query()]
) -> dict[str, Any]:
    """Total net_value, quantity and row_count, plus groups when group_by is set."""
    return service.summarize(params)
