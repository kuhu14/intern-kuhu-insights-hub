from typing import Any

from app.repositories.sales_repository import SalesFilters, SalesRepository


class SalesService:
    """Business logic between the routers and the repository."""

    def __init__(self, repository: SalesRepository) -> None:
        self._repository = repository

    def list_sales(
        self, filters: SalesFilters, page: int, page_size: int
    ) -> dict[str, Any]:
        items, total = self._repository.filter(filters, page=page, page_size=page_size)
        return {"items": items, "page": page, "page_size": page_size, "total": total}

    def summarize(self, filters: SalesFilters, group_by: str | None) -> dict[str, Any]:
        return self._repository.aggregate(filters, group_by=group_by)

    def regions(self) -> list[str]:
        return self._repository.regions()

    def brands(self) -> list[str]:
        return self._repository.brands()

    def skus(self) -> list[dict[str, Any]]:
        return self._repository.skus()

    def distributors(self) -> list[dict[str, Any]]:
        return self._repository.distributors()
