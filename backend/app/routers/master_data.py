from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.dependencies import get_sales_service
from app.services.sales_service import SalesService

router = APIRouter(tags=["master data"])

ServiceDep = Annotated[SalesService, Depends(get_sales_service)]


@router.get("/regions", summary="List regions")
def list_regions(service: ServiceDep) -> list[str]:
    """Distinct regions found in the sales data."""
    return service.regions()


@router.get("/brands", summary="List brands")
def list_brands(service: ServiceDep) -> list[str]:
    """Distinct brands found in the sales data."""
    return service.brands()


@router.get("/skus", summary="List SKUs")
def list_skus(service: ServiceDep) -> list[dict[str, Any]]:
    """Distinct SKUs with their name and brand."""
    return service.skus()


@router.get("/distributors", summary="List distributors")
def list_distributors(service: ServiceDep) -> list[dict[str, Any]]:
    """Distinct distributors with their name, region and state."""
    return service.distributors()
