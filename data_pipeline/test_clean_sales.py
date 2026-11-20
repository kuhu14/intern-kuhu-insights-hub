"""Each test uses small sample dataframes to test the cleaning functions in clean_sales.py."""

import math
from datetime import date, datetime
import pandas as pd
import pytest

from clean_sales import (
    add_is_return,
    normalise_region,
    parse_amount,
    parse_date,
    remove_duplicates,
    remove_test_rows,
    split_rejects,
)

BLANK = float("nan")
@pytest.fixture
def tiny_sales():
    """8 rows of sample data to test the cleaning functions."""
    return pd.DataFrame(
        {
            "Invoice No": [
                "INV-001",
                "INV-001",
                "INV-002",
                "INV-003",
                "INV-004",
                "INV-005",
                "INV-006",
                "CN-007",
            ],
            "Dist Code": [
                "D001",
                "D001",
                "D999",
                "D001",
                "D001",
                "D001",
                "D001",
                "D001"
            ],
            "Qty": [10, 10, 5, BLANK, 4, -5, 1500, -3],
            "Net Value (INR)": [
                1000.0,
                1000.0,
                500.0,
                300.0,
                BLANK,
                -500.0,
                9000.0,
                -300.0
            ],
        }
    )

def test_parse_date_handles_all_formates():
    assert parse_date("15/07/2026") == date(2026, 7, 15)
    assert parse_date("10-Jul-25") == date(2025, 7, 10)
    assert parse_date("2026-09-28") == date(2026, 9, 28)
    assert parse_date(datetime(2026, 6, 26)) == date(2026, 6, 26)

def test_parse_date_is_day_first():
    assert parse_date("01/02/2026") == date(2026, 2, 1)
    assert parse_date("02/01/2026") == date(2026, 1, 2)

def test_parse_amount():
    assert parse_amount("₹12,345.60") == 12345.6
    assert parse_amount(500) == 500.0
    assert math.isnan(parse_amount(BLANK))

@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("north", "North"),
        ("NORTH", "North"),
        ("N", "North"),
        ("e", "East"),
        ("South", "South"),
        ("w", "West"),
    ],
)
def test_normalise_region(raw, expected):
    assert normalise_region(raw) == expected

def test_unknown_region_fails_loudly():
    with pytest.raises(KeyError):
        normalise_region("Central")

def test_remove_duplicates(tiny_sales):
    result = remove_duplicates(tiny_sales)
    assert len(result) == 7
    assert (result["Invoice No"] == "INV-001").sum() == 1

def test_remove_test_rows(tiny_sales):
    result = remove_test_rows(tiny_sales)
    assert "D999" not in result["Dist Code"].values
    assert len(result) == 7

def test_reject_classification(tiny_sales):
    df = add_is_return(tiny_sales)
    clean, rejects = split_rejects(df)
    reasons = dict(zip(rejects["Invoice No"], rejects["reason"]))
    assert reasons == {
        "INV-003": "blank_qty",
        "INV-004": "blank_net_value",
        "INV-005": "negative_qty_not_credit_note",
        "INV-006": "qty_over_1000",
    }

def test_credit_note_is_kept(tiny_sales):
    df = add_is_return(tiny_sales)
    clean, rejects = split_rejects(df)
    credit_note = clean[clean["Invoice No"] == "CN-007"]
    assert len(credit_note) == 1
    assert bool(credit_note["is_return"].iloc[0]) is True
    assert "CN-007" not in rejects["Invoice No"].values
