from typing import Any, Protocol

from app.repositories.sales_repository import SalesFilters


class SalesRepositoryProtocol(Protocol):
    """The public methods every sales repository must have.

    SalesRepository (CSV file) and PostgresSalesRepository both match this, so the
    service and routers work with either one without knowing which it is.
    """

    def filter(
        self, filters: SalesFilters, page: int = 1, page_size: int = 50
    ) -> tuple[list[dict[str, Any]], int]: ...

    def aggregate(
        self, filters: SalesFilters, group_by: str | None = None
    ) -> dict[str, Any]: ...

    def sku_exists(self, sku_code: str) -> bool: ...

    def regions(self) -> list[str]: ...

    def brands(self) -> list[str]: ...

    def skus(self) -> list[dict[str, Any]]: ...

    def distributors(self) -> list[dict[str, Any]]: ...
