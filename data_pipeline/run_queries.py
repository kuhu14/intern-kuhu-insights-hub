"""Load clean_sales.csv into SQLite (data_pipeline/output/sales.db) and run every query in queries.sql.

Run from the project root:  python data_pipeline/run_queries.py
"""
import sqlite3
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
CLEAN_CSV = HERE / "output" / "clean_sales.csv"
DB_PATH = HERE / "output" / "sales.db"
QUERIES_PATH = HERE / "queries.sql"

def load_to_sqlite(csv_path: Path, db_path: Path):
    """Load the cleaned sales data into a SQLite database."""
    df = pd.read_csv(csv_path)
    with sqlite3.connect(db_path) as conn:
        df.to_sql("sales", conn, if_exists="replace", index=False)
    return len(df)

def split_queries(sql_text):
    """Split queries.sql into separate statements on ';'"""
    return [q.strip() for q in sql_text.split(";") if q.strip()]

def main():
    rows = load_to_sqlite(CLEAN_CSV, DB_PATH)
    print(f"Loaded {rows} rows into {DB_PATH.name}\n")

    queries = split_queries(QUERIES_PATH.read_text(encoding="utf-8"))
    with sqlite3.connect(DB_PATH) as conn:
        for query in queries:
            print(query)
            print(pd.read_sql_query(query, conn).to_string(index=False))
            print()

if __name__ == "__main__":
    main()
