import re
from datetime import date
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.enums import Channel, GroupBy, Region

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ---------- request models (query parameters) ----------


class SalesFilterParams(BaseModel):
    """Filters shared by GET /sales and GET /sales/summary."""

    region: Region | None = Field(None, description="Region to filter by")
    state: str | None = Field(None, description="State, e.g. Bihar")
    brand: str | None = Field(None, description="Brand, e.g. Navratna")
    sku_code: str | None = Field(None, description="SKU code, e.g. EM-1003")
    channel: Channel | None = Field(None, description="Sales channel")
    date_from: date | None = Field(
        None, description="Start date (YYYY-MM-DD), inclusive"
    )
    date_to: date | None = Field(None, description="End date (YYYY-MM-DD), inclusive")
    is_return: bool | None = Field(
        None, description="true = only returns, false = only sales"
    )

    @field_validator("date_from", "date_to", mode="before")
    @classmethod
    def require_iso_date(cls, value: Any) -> Any:
        if value is not None and not (
            isinstance(value, str) and DATE_PATTERN.match(value)
        ):
            raise ValueError("date must be in YYYY-MM-DD format")
        return value

    @model_validator(mode="after")
    def check_date_range(self) -> "SalesFilterParams":
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be on or before date_to")
        return self


class SalesListParams(SalesFilterParams):
    """Query parameters for GET /sales."""

    page: int = Field(1, ge=1, description="Page number, starts at 1")
    page_size: int = Field(50, ge=1, le=200, description="Rows per page (max 200)")


class SalesSummaryParams(SalesFilterParams):
    """Query parameters for GET /sales/summary."""

    group_by: GroupBy | None = Field(
        None, description="Optional grouping for per-group totals"
    )


# ---------- response models ----------


class SaleItem(BaseModel):
    invoice_no: str
    invoice_date: date
    region: Region
    state: str
    dist_code: str
    distributor_name: str
    sku_code: str
    sku_name: str
    brand: str
    channel: Channel
    qty: float
    net_value: float
    is_return: bool


class SalesPage(BaseModel):
    items: list[SaleItem]
    page: int
    page_size: int
    total: int = Field(description="Total rows matching the filters, across all pages")


class SummaryGroup(BaseModel):
    key: str = Field(description="Group value, e.g. North or 2025-12")
    net_value: float
    quantity: float
    row_count: int


class SalesSummary(BaseModel):
    net_value: float
    quantity: float
    row_count: int
    groups: list[SummaryGroup] | None = Field(
        None, description="Per-group totals; only present when group_by is set"
    )
