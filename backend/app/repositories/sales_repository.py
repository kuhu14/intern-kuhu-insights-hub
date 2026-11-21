from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

# Maps the public group_by names to the column used for grouping.
GROUP_COLUMNS: dict[str, str] = {
    "region": "region",
    "state": "state",
    "brand": "brand",
    "sku": "sku_code",
    "channel": "channel",
    "month": "month",
}


@dataclass(frozen=True)
class SalesFilters:
    """Optional filters shared by filter() and aggregate(). None means 'no filter'."""

    region: str | None = None
    state: str | None = None
    brand: str | None = None
    sku_code: str | None = None
    channel: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    is_return: bool | None = None


class SalesRepository:
    """The only place in the app that touches pandas or the CSV file."""

    def __init__(self, csv_path: Path) -> None:
        df = pd.read_csv(csv_path)
        df["invoice_date"] = pd.to_datetime(df["invoice_date"], format="%Y-%m-%d")
        df["month"] = df["invoice_date"].dt.strftime("%Y-%m")
        # Stable order so pagination always returns the same rows per page.
        self._df = df.sort_values(["invoice_date", "invoice_no"]).reset_index(drop=True)

    def _apply_filters(self, filters: SalesFilters) -> pd.DataFrame:
        df = self._df
        mask = pd.Series(True, index=df.index)

        for column in ("region", "state", "brand", "sku_code", "channel"):
            value = getattr(filters, column)
            if value is not None:
                mask &= df[column] == value

        if filters.date_from is not None:
            mask &= df["invoice_date"] >= pd.Timestamp(filters.date_from)
        if filters.date_to is not None:
            # date_to is inclusive; dates have no time part, so <= is enough.
            mask &= df["invoice_date"] <= pd.Timestamp(filters.date_to)
        if filters.is_return is not None:
            mask &= df["is_return"] == filters.is_return

        return df[mask]

    def filter(
        self, filters: SalesFilters, page: int = 1, page_size: int = 50
    ) -> tuple[list[dict[str, Any]], int]:
        """Return (rows for the requested page, total matching rows)."""
        matched = self._apply_filters(filters)
        total = len(matched)

        start = (page - 1) * page_size
        page_df = matched.iloc[start : start + page_size].drop(columns=["month"])
        page_df = page_df.assign(
            invoice_date=page_df["invoice_date"].dt.strftime("%Y-%m-%d")
        )
        return page_df.to_dict(orient="records"), total

    def aggregate(
        self, filters: SalesFilters, group_by: str | None = None
    ) -> dict[str, Any]:
        """Return overall totals, plus per-group totals when group_by is given."""
        matched = self._apply_filters(filters)
        result: dict[str, Any] = {
            "net_value": round(float(matched["net_value"].sum()), 2),
            "quantity": int(matched["qty"].sum()),
            "row_count": len(matched),
            "groups": None,
        }

        if group_by is not None:
            column = GROUP_COLUMNS[group_by]
            grouped = (
                matched.groupby(column)
                .agg(
                    net_value=("net_value", "sum"),
                    quantity=("qty", "sum"),
                    row_count=("invoice_no", "count"),
                )
                .sort_index()
            )
            result["groups"] = [
                {
                    "key": str(key),
                    "net_value": round(float(row.net_value), 2),
                    "quantity": int(row.quantity),
                    "row_count": int(row.row_count),
                }
                for key, row in grouped.iterrows()
            ]

        return result

    def sku_exists(self, sku_code: str) -> bool:
        return bool((self._df["sku_code"] == sku_code).any())


    def _distinct(self, columns: list[str]) -> list[dict[str, Any]]:
        unique_rows = self._df[columns].drop_duplicates().sort_values(columns)
        return unique_rows.to_dict(orient="records")

    def regions(self) -> list[str]:
        return [row["region"] for row in self._distinct(["region"])]

    def brands(self) -> list[str]:
        return [row["brand"] for row in self._distinct(["brand"])]

    def skus(self) -> list[dict[str, Any]]:
        return self._distinct(["sku_code", "sku_name", "brand"])

    def distributors(self) -> list[dict[str, Any]]:
        return self._distinct(["dist_code", "distributor_name", "region", "state"])
