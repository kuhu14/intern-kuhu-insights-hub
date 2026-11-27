"""Week 4: the seeded Postgres database, the view and the constraints.

Needs Postgres with "alembic upgrade head" and "python scripts/seed_db.py" done.
Skipped when the database is not reachable. Every test runs inside a transaction
that is rolled back, so nothing here changes the data.
"""

from datetime import date
from decimal import Decimal
from typing import Any

import pytest
from sqlalchemy import func, insert, select, text
from sqlalchemy.exc import IntegrityError

from app.db.models import Brand, Distributor, Region, Sale, Sku, State


def a_sale(**changes: Any) -> dict[str, Any]:
    """A valid sale for distributor 1 and SKU 1; pass keyword args to break it."""
    sale = {
        "invoice_no": "TEST-0001",
        "invoice_date": date(2025, 1, 15),
        "distributor_id": 1,
        "sku_id": 1,
        "channel": "Chemist",
        "quantity": 5,
        "net_value": Decimal("100.00"),
        "is_return": False,
    }
    return sale | changes


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        (Region, 4),
        (State, 12),
        (Distributor, 24),
        (Brand, 8),
        (Sku, 23),
        (Sale, 5418),
    ],
)
def test_row_counts_after_seeding(db_conn, model, expected):
    assert db_conn.scalar(select(func.count()).select_from(model)) == expected


def test_sales_totals_after_seeding(db_conn):
    assert db_conn.scalar(select(func.sum(Sale.net_value))) == Decimal("60984552.24")
    assert db_conn.scalar(select(func.count()).where(Sale.is_return)) == 78


def test_view_net_value_by_region(db_conn):
    rows = db_conn.execute(
        text("SELECT region, SUM(net_value) FROM v_sales_denorm GROUP BY region")
    )
    assert dict(rows.all()) == {
        "East": Decimal("11979450.64"),
        "North": Decimal("14621494.11"),
        "South": Decimal("15657120.63"),
        "West": Decimal("18726486.86"),
    }


def test_valid_sale_is_accepted(db_conn):
    db_conn.execute(insert(Sale).values(a_sale()))
    count = select(func.count()).where(Sale.invoice_no == "TEST-0001")
    assert db_conn.scalar(count) == 1


def test_return_with_positive_quantity_is_rejected(db_conn):
    with pytest.raises(IntegrityError, match="ck_sales_return_quantity_sign"):
        db_conn.execute(insert(Sale).values(a_sale(is_return=True, quantity=5)))


def test_sale_with_negative_quantity_is_rejected(db_conn):
    with pytest.raises(IntegrityError, match="ck_sales_return_quantity_sign"):
        db_conn.execute(insert(Sale).values(a_sale(is_return=False, quantity=-5)))


def test_sale_for_missing_sku_is_rejected(db_conn):
    with pytest.raises(IntegrityError, match="fk_sales_sku_id_skus"):
        db_conn.execute(insert(Sale).values(a_sale(sku_id=999_999)))


def test_sale_for_missing_distributor_is_rejected(db_conn):
    with pytest.raises(IntegrityError, match="fk_sales_distributor_id_distributors"):
        db_conn.execute(insert(Sale).values(a_sale(distributor_id=999_999)))
