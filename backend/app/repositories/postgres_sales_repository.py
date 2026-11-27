"""Sales repository backed by Postgres (the v_sales_denorm view and master tables).

Same public methods and return shapes as the CSV-backed SalesRepository, so the
service, routers and tests do not change.
"""

from typing import Any

from sqlalchemy import (
    Boolean,
    ColumnElement,
    Date,
    Engine,
    Integer,
    Numeric,
    Select,
    String,
    column,
    func,
    literal,
    select,
    table,
)

from app.db.models import Brand, Distributor, Region, Sku, State
from app.repositories.sales_repository import SalesFilters

# The view is not a model (Alembic must not try to create it), so describe the
# columns we read from it here.
v_sales = table(
    "v_sales_denorm",
    column("invoice_no", String),
    column("invoice_date", Date),
    column("region", String),
    column("state", String),
    column("dist_code", String),
    column("distributor_name", String),
    column("sku_code", String),
    column("sku_name", String),
    column("brand", String),
    column("channel", String),
    column("qty", Integer),
    column("net_value", Numeric(12, 2)),
    column("is_return", Boolean),
)

# The columns returned for each sale, in the Week 3 API order.
SALE_COLUMNS = [
    "invoice_no",
    "invoice_date",
    "region",
    "state",
    "dist_code",
    "distributor_name",
    "sku_code",
    "sku_name",
    "brand",
    "channel",
    "qty",
    "net_value",
    "is_return",
]

# Maps the public group_by names to the expression used for grouping.
GROUP_EXPRESSIONS: dict[str, ColumnElement[Any]] = {
    "region": v_sales.c.region,
    "state": v_sales.c.state,
    "brand": v_sales.c.brand,
    "sku": v_sales.c.sku_code,
    "channel": v_sales.c.channel,
    "month": func.to_char(v_sales.c.invoice_date, "YYYY-MM"),
}


def _sorted(expression: ColumnElement[Any]) -> ColumnElement[Any]:
    # COLLATE "C" sorts by plain character codes, like Python's sorted(), so the
    # order matches the file repository whatever the database's locale is.
    return expression.collate("C")


class PostgresSalesRepository:
    """Reads sales from Postgres. All SQL in the app lives here."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def _where(self, query: Select, filters: SalesFilters) -> Select:
        for name in ("region", "state", "brand", "sku_code", "channel"):
            value = getattr(filters, name)
            if value is not None:
                # str() turns enums such as Channel.GENERAL_TRADE into "General Trade".
                query = query.where(v_sales.c[name] == str(value))

        if filters.date_from is not None:
            query = query.where(v_sales.c.invoice_date >= filters.date_from)
        if filters.date_to is not None:
            # date_to is inclusive, the same as the file repository.
            query = query.where(v_sales.c.invoice_date <= filters.date_to)
        if filters.is_return is not None:
            query = query.where(v_sales.c.is_return == filters.is_return)

        return query

    def filter(
        self, filters: SalesFilters, page: int = 1, page_size: int = 50
    ) -> tuple[list[dict[str, Any]], int]:
        """Return (rows for the requested page, total matching rows)."""
        count_query = self._where(select(func.count()).select_from(v_sales), filters)
        page_query = (
            self._where(select(*(v_sales.c[name] for name in SALE_COLUMNS)), filters)
            # Stable order so pagination always returns the same rows per page.
            .order_by(v_sales.c.invoice_date, v_sales.c.invoice_no)
            .limit(page_size)
            .offset((page - 1) * page_size)
        )

        with self._engine.connect() as conn:
            total = conn.scalar(count_query)
            rows = conn.execute(page_query).mappings().all()

        items = [
            {
                **row,
                "invoice_date": row["invoice_date"].isoformat(),
                "qty": float(row["qty"]),
                "net_value": float(row["net_value"]),
            }
            for row in rows
        ]
        return items, total

    def aggregate(
        self, filters: SalesFilters, group_by: str | None = None
    ) -> dict[str, Any]:
        """Return overall totals, plus per-group totals when group_by is given."""
        measures = [
            func.coalesce(func.sum(v_sales.c.net_value), 0).label("net_value"),
            func.coalesce(func.sum(v_sales.c.qty), 0).label("quantity"),
            func.count().label("row_count"),
        ]
        totals_query = self._where(select(*measures).select_from(v_sales), filters)

        with self._engine.connect() as conn:
            totals = conn.execute(totals_query).one()
            result: dict[str, Any] = {
                "net_value": round(float(totals.net_value), 2),
                "quantity": float(totals.quantity),
                "row_count": totals.row_count,
                "groups": None,
            }

            if group_by is not None:
                key = GROUP_EXPRESSIONS[group_by].label("key")
                groups_query = (
                    self._where(select(key, *measures).select_from(v_sales), filters)
                    .group_by(key)
                    .order_by(_sorted(key))
                )
                result["groups"] = [
                    {
                        "key": str(row.key),
                        "net_value": round(float(row.net_value), 2),
                        "quantity": float(row.quantity),
                        "row_count": row.row_count,
                    }
                    for row in conn.execute(groups_query)
                ]

        return result

    def sku_exists(self, sku_code: str) -> bool:
        query = select(literal(True)).where(Sku.sku_code == sku_code)
        with self._engine.connect() as conn:
            return conn.scalar(query) is not None

    def regions(self) -> list[str]:
        query = select(Region.region_name).order_by(_sorted(Region.region_name))
        with self._engine.connect() as conn:
            return list(conn.scalars(query))

    def brands(self) -> list[str]:
        query = select(Brand.brand_name).order_by(_sorted(Brand.brand_name))
        with self._engine.connect() as conn:
            return list(conn.scalars(query))

    def skus(self) -> list[dict[str, Any]]:
        query = (
            select(Sku.sku_code, Sku.sku_name, Brand.brand_name.label("brand"))
            .join(Brand, Sku.brand_id == Brand.brand_id)
            .order_by(_sorted(Sku.sku_code))
        )
        with self._engine.connect() as conn:
            return [dict(row) for row in conn.execute(query).mappings()]

    def distributors(self) -> list[dict[str, Any]]:
        query = (
            select(
                Distributor.distributor_code.label("dist_code"),
                Distributor.distributor_name,
                Region.region_name.label("region"),
                State.state_name.label("state"),
            )
            .join(State, Distributor.state_id == State.state_id)
            .join(Region, State.region_id == Region.region_id)
            .order_by(_sorted(Distributor.distributor_code))
        )
        with self._engine.connect() as conn:
            return [dict(row) for row in conn.execute(query).mappings()]
