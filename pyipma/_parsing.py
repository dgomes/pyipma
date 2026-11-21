"""Shared normalization for optional values in IPMA responses."""

from typing import Any, TypeVar

Number = TypeVar("Number", int, float)


def number(value: Any, number_type: type[Number]) -> Number | None:
    """Preserve zero, normalize missing values, and reject malformed numbers."""
    if value is None or value == "" or float(value) == -99:
        return None
    return number_type(value)


def text(value: str | int | float | None) -> str | None:
    """Normalize missing text such as wind direction without inventing a value."""
    if value in (None, "", -99, "-99", "-99.0"):
        return None
    return str(value)
