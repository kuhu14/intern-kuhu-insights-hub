from datetime import date, datetime
from decimal import Decimal

import pytest

from warmup.utils import fiscal_year, format_inr, parse_pack_size

# ---------- fiscal_year ----------


@pytest.mark.parametrize(
    ("d", "expected"),
    [
        (date(2026, 3, 31), "FY2025-26"),  # last day of FY
        (date(2026, 4, 1), "FY2026-27"),  # first day of next FY
        (date(2025, 12, 15), "FY2025-26"),  # mid-year
        (date(2026, 1, 1), "FY2025-26"),  # calendar year change, same FY
        (date(1999, 4, 1), "FY1999-00"),  # century wrap
    ],
)
def test_fiscal_year(d, expected):
    assert fiscal_year(d) == expected


def test_fiscal_year_accepts_datetime():
    assert fiscal_year(datetime(2026, 4, 1, 9, 30)) == "FY2026-27"


def test_fiscal_year_rejects_non_date():
    with pytest.raises(TypeError):
        fiscal_year("2026-04-01")


# ---------- format_inr ----------


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (6098455224 / 100, "6,09,84,552.24"),
        (0, "0.00"),
        (999, "999.00"),
        (1000, "1,000.00"),
        (100000, "1,00,000.00"),
        (12345678.9, "1,23,45,678.90"),
        (Decimal("2.345"), "2.35"),  # rounds half up
        (-150000.5, "-1,50,000.50"),
    ],
)
def test_format_inr(amount, expected):
    assert format_inr(amount) == expected


def test_format_inr_rejects_non_number():
    with pytest.raises(TypeError):
        format_inr("1000")


# ---------- parse_pack_size ----------


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("200 ml", (200, "ml")),
        ("200ml", (200, "ml")),
        ("  50 G ", (50, "g")),
        ("1.5 L", (1.5, "l")),
    ],
)
def test_parse_pack_size(text, expected):
    assert parse_pack_size(text) == expected


def test_parse_pack_size_returns_int_for_whole_numbers():
    quantity, _ = parse_pack_size("200 ml")
    assert isinstance(quantity, int)


@pytest.mark.parametrize("text", ["", "ml", "200", "200 m l", "-5 ml", "abc ml"])
def test_parse_pack_size_rejects_bad_input(text):
    with pytest.raises(ValueError):
        parse_pack_size(text)
