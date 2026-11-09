"""Python warm-up helpers for Indian sales data."""

import re
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

_PACK_SIZE_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([A-Za-z]+)\s*$")


def fiscal_year(d: date) -> str:
    """Return the Indian fiscal year (April to March) for a date.

    >>> fiscal_year(date(2026, 3, 31))
    'FY2025-26'
    >>> fiscal_year(date(2026, 4, 1))
    'FY2026-27'
    """
    if not isinstance(d, date):
        raise TypeError(f"expected a date, got {type(d).__name__}")
    start = d.year if d.month >= 4 else d.year - 1
    return f"FY{start}-{(start + 1) % 100:02d}"


def format_inr(amount: float | int | Decimal) -> str:
    """Format a number with Indian digit grouping and 2 decimals.

    The last 3 digits form one group, then every 2 digits after that.

    >>> format_inr(6098455224 / 100)
    '6,09,84,552.24'
    """
    if isinstance(amount, bool) or not isinstance(amount, int | float | Decimal):
        raise TypeError(f"expected a number, got {type(amount).__name__}")
    # str() first so floats like 0.1 are not expanded to 0.1000000000000000055...
    value = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    sign = "-" if value < 0 else ""
    whole, fraction = f"{abs(value):.2f}".split(".")

    head, tail = whole[:-3], whole[-3:]
    groups = []
    while head:
        groups.insert(0, head[-2:])
        head = head[:-2]
    groups.append(tail)
    return f"{sign}{','.join(groups)}.{fraction}"


def parse_pack_size(text: str) -> tuple[int | float, str]:
    """Split a pack size like "200 ml" into (200, "ml").

    Whole numbers come back as int, decimals as float. The unit is lower-cased.

    >>> parse_pack_size("200 ml")
    (200, 'ml')
    >>> parse_pack_size("1.5L")
    (1.5, 'l')
    """
    if not isinstance(text, str):
        raise TypeError(f"expected a string, got {type(text).__name__}")
    match = _PACK_SIZE_RE.match(text)
    if not match:
        raise ValueError(f"invalid pack size: {text!r}")
    number, unit = match.groups()
    quantity = float(number) if "." in number else int(number)
    return quantity, unit.lower()
