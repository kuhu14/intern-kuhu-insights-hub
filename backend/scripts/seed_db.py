"""Load the five master sheets and the clean sales CSV into Postgres.

Run from backend/ after "alembic upgrade head", either way:

    python scripts/seed_db.py
    python -m scripts.seed_db

Idempotent: every row is upserted on its natural key (region_name, state_name,
distributor_code, brand_name, sku_code, invoice_no), so running it twice leaves
the same row counts.
"""

import sys
from decimal import Decimal
from pathlib import Path

# Let "python scripts/seed_db.py" find the app package (backend/ on sys.path).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402
from sqlalchemy import Connection, func, select  # noqa: E402
from sqlalchemy.dialects.postgresql import insert  # noqa: E402

from app.config import REPO_ROOT, settings  # noqa: E402
from app.db.models import Brand, Distributor, Region, Sale, Sku, State  # noqa: E402
from app.db.session import engine  # noqa: E402

MASTERS_XLSX = REPO_ROOT / "datasets" / "week04" / "week04_masters.xlsx"
BATCH_SIZE = 1000

# Load order matters: parents before children. (model, natural key column)
MASTER_TABLES = [
    (Region, "region_name"),
    (State, "state_name"),
    (Distributor, "distributor_code"),
    (Brand, "brand_name"),
    (Sku, "sku_code"),
]


def upsert(conn: Connection, model, rows: list[dict], key: str) -> None:
    """INSERT ... ON CONFLICT (key) DO UPDATE, in batches."""
    for start in range(0, len(rows), BATCH_SIZE):
        stmt = insert(model).values(rows[start : start + BATCH_SIZE])
        primary_key = model.__table__.primary_key.columns.keys()[0]
        update_columns = {
            name: stmt.excluded[name]
            for name in rows[0]
            if name not in (key, primary_key)
        }
        if update_columns:
            stmt = stmt.on_conflict_do_update(index_elements=[key], set_=update_columns)
        else:
            # e.g. regions: only id + name, so an existing row needs no update.
            stmt = stmt.on_conflict_do_nothing(index_elements=[key])
        conn.execute(stmt)


def load_masters(conn: Connection) -> None:
    sheets = pd.read_excel(MASTERS_XLSX, sheet_name=None)
    for model, key in MASTER_TABLES:
        df = sheets[model.__tablename__]
        if "mrp" in df.columns:
            # Money as exact Decimal, never float.
            df["mrp"] = df["mrp"].map(lambda value: Decimal(str(value)))
        rows = df.astype(object).to_dict(orient="records")
        upsert(conn, model, rows, key)


def load_sales(conn: Connection) -> None:
    # Read net_value as text so it becomes an exact Decimal, not a float.
    df = pd.read_csv(settings.sales_csv_path, dtype={"net_value": str})

    # Map the natural codes in the CSV to the ids in the master tables.
    distributor_ids = dict(
        conn.execute(
            select(Distributor.distributor_code, Distributor.distributor_id)
        ).all()
    )
    sku_ids = dict(conn.execute(select(Sku.sku_code, Sku.sku_id)).all())
    unknown_distributors = set(df["dist_code"]) - distributor_ids.keys()
    unknown_skus = set(df["sku_code"]) - sku_ids.keys()
    if unknown_distributors or unknown_skus:
        raise SystemExit(
            f"Unknown codes in CSV: distributors={sorted(unknown_distributors)} "
            f"skus={sorted(unknown_skus)}"
        )

    rows = [
        {
            "invoice_no": row.invoice_no,
            "invoice_date": pd.Timestamp(row.invoice_date).date(),
            "distributor_id": distributor_ids[row.dist_code],
            "sku_id": sku_ids[row.sku_code],
            "channel": row.channel,
            "quantity": int(row.qty),
            "net_value": Decimal(row.net_value),
            "is_return": bool(row.is_return),
        }
        for row in df.itertuples(index=False)
    ]
    upsert(conn, Sale, rows, "invoice_no")


def print_summary(conn: Connection) -> None:
    print("Row counts:")
    for model, _ in [*MASTER_TABLES, (Sale, None)]:
        count = conn.scalar(select(func.count()).select_from(model))
        print(f"  {model.__tablename__:<13} {count:>6,}")
    total = conn.scalar(select(func.sum(Sale.net_value)))
    returns = conn.scalar(select(func.count()).where(Sale.is_return))
    print(f"SUM(net_value)  {total}")
    print(f"Returns         {returns}")


def main() -> None:
    # One transaction: if anything fails, nothing is half-loaded.
    with engine.begin() as conn:
        load_masters(conn)
        load_sales(conn)
        print_summary(conn)


if __name__ == "__main__":
    main()
