from typing import Any

from app.errors import NotFoundError
from app.repositories.protocol import SalesRepositoryProtocol
from app.repositories.sales_repository import SalesFilters
from app.schemas.sales import SalesFilterParams, SalesListParams, SalesSummaryParams


def to_filters(params: SalesFilterParams) -> SalesFilters:
    """Turn validated API query parameters into the repository's filter object."""
    return SalesFilters(
        region=params.region,
        state=params.state,
        brand=params.brand,
        sku_code=params.sku_code,
        channel=params.channel,
        date_from=params.date_from,
        date_to=params.date_to,
        is_return=params.is_return,
    )


class SalesService:
    """Business logic between the routers and the repository."""

    def __init__(self, repository: SalesRepositoryProtocol) -> None:
        self._repository = repository

    def _check_sku(self, sku_code: str | None) -> None:
        if sku_code is not None and not self._repository.sku_exists(sku_code):
            raise NotFoundError("SKU_NOT_FOUND", f"Unknown sku_code: {sku_code}")

    def list_sales(self, params: SalesListParams) -> dict[str, Any]:
        self._check_sku(params.sku_code)
        items, total = self._repository.filter(
            to_filters(params), page=params.page, page_size=params.page_size
        )
        return {
            "items": items,
            "page": params.page,
            "page_size": params.page_size,
            "total": total,
        }

    def summarize(self, params: SalesSummaryParams) -> dict[str, Any]:
        self._check_sku(params.sku_code)
        return self._repository.aggregate(to_filters(params), group_by=params.group_by)

    def regions(self) -> list[str]:
        return self._repository.regions()

    def brands(self) -> list[str]:
        return self._repository.brands()

    def skus(self) -> list[dict[str, Any]]:
        return self._repository.skus()

    def distributors(self) -> list[dict[str, Any]]:
        return self._repository.distributors()
