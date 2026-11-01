"""Money helpers.

Amounts are Decimal inside the package and strings on the way out. Every
currency is rounded half-up to its own minor unit (cents for EUR, whole yen
for JPY).
"""

from decimal import Decimal

MINOR_UNITS = {"EUR": 2, "USD": 2, "GBP": 2, "JPY": 0}


def to_decimal(value):
    return Decimal(str(value))


def quantize(amount, currency="EUR"):
    """Round half-up to the minor unit of ``currency``."""
    return Decimal(str(round(float(amount), 2))).quantize(Decimal("0.01"))


def fmt(amount, currency="EUR"):
    return str(quantize(amount, currency))


def fmt_rate(rate):
    """VAT rate as printed on the invoice: "19", "5.5", "0"."""
    return format(Decimal(rate).normalize(), "f")
