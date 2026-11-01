"""Money: Decimal inside, strings with two decimals outside, rounded half-up to kopecks."""

from decimal import Decimal


def to_money(value):
    return Decimal(str(value))


def round_kop(amount):
    return Decimal(str(round(float(amount), 2))).quantize(Decimal("0.01"))


def fmt(amount):
    return str(round_kop(amount))
