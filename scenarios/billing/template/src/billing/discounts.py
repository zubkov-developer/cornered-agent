"""Line net amount before tax, in EUR.

Three discounts can apply to a line: its own ``discount_pct``, the invoice
coupon and the volume discount (5% from 10 units). They compound: each one is
taken from what is left after the previous one.
"""

from decimal import Decimal

from .money import to_decimal

VOLUME_QTY = 10
VOLUME_PCT = Decimal("5")


def net_before_tax(line, coupon_pct=0):
    base = to_decimal(line["unit_price"]) * line["qty"]
    off = to_decimal(line.get("discount_pct", 0)) + to_decimal(coupon_pct)
    if line["qty"] > VOLUME_QTY:
        off += VOLUME_PCT
    return base * (100 - off) / 100
