"""Money: Decimal inside, strings with two decimals outside, rounded half-up to kopecks."""

from decimal import Decimal, ROUND_HALF_UP


def to_money(value):
    return Decimal(str(value))


def round_kop(amount):
    return Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def fmt(amount):
    return str(round_kop(amount))
