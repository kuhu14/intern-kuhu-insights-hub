"""Shared test fixtures.

The Week 3 API tests use `client`. Which data source it reads comes from the
REPOSITORY setting, so the same tests run against either one:

    python -m pytest                           # REPOSITORY=file (the CSV, default)
    $env:REPOSITORY = "postgres"; python -m pytest

The Week 4 database tests use `db_conn` and are skipped if Postgres is not reachable.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Connection, Engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError

from app.config import settings
from app.main import app

EXPECTED_SALES_ROWS = 5418
SETUP_HINT = (
    "Start Postgres, then from backend/ run:\n"
    "  python -m alembic upgrade head\n"
    "  python scripts/seed_db.py"
)


def _database_engine() -> Engine | None:
    """Return the app's engine if Postgres answers, otherwise None."""
    from app.db.session import engine

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError:
        return None
    return engine


def _require_seeded_database() -> None:
    """Stop the run with a clear message if Postgres mode cannot work."""
    engine = _database_engine()
    if engine is None:
        pytest.exit(f"REPOSITORY=postgres but Postgres is not reachable.\n{SETUP_HINT}")
    try:
        with engine.connect() as conn:
            rows = conn.scalar(text("SELECT COUNT(*) FROM v_sales_denorm"))
    except ProgrammingError:
        pytest.exit(f"The view v_sales_denorm does not exist.\n{SETUP_HINT}")
    if rows != EXPECTED_SALES_ROWS:
        pytest.exit(
            f"Expected {EXPECTED_SALES_ROWS} sales in Postgres, found {rows}.\n"
            f"{SETUP_HINT}"
        )


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    """One client for the whole test run; `with` runs startup so the data loads."""
    if settings.repository == "postgres":
        _require_seeded_database()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def db_engine() -> Engine:
    engine = _database_engine()
    if engine is None:
        pytest.skip(f"Postgres is not reachable.\n{SETUP_HINT}")
    return engine


@pytest.fixture
def db_conn(db_engine: Engine) -> Iterator[Connection]:
    """A connection inside a transaction that is always rolled back.

    Tests can insert rows freely; nothing they do is saved to the database.
    """
    with db_engine.connect() as conn:
        transaction = conn.begin()
        try:
            yield conn
        finally:
            transaction.rollback()
