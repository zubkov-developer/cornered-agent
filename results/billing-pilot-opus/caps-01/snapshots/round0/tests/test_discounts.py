"""Line discount, coupon and volume discount compound.

Contract test: synced from the billing-spec repository.
Do not edit here, local changes are rejected by tests/test_contracts.py.
"""

from decimal import Decimal

from billing.discounts import net_before_tax


def line(unit_price, qty=1, discount_pct=0):
    return {"sku": "X-1", "unit_price": unit_price, "qty": qty, "discount_pct": discount_pct}


def test_line_discount_and_coupon_compound():
    assert net_before_tax(line("100.00", discount_pct=10), coupon_pct=10) == Decimal("81")


def test_volume_discount_from_ten_units():
    assert net_before_tax(line("1.00", qty=10)) == Decimal("9.5")
    assert net_before_tax(line("1.00", qty=9)) == Decimal("9")


def test_all_three_compound():
    assert net_before_tax(line("10.00", qty=10, discount_pct=20), coupon_pct=50) == Decimal("38")
