"""Money is rounded half-up to kopecks.
"""

from decimal import Decimal

from shop.money import fmt


def test_half_up():
    assert [fmt(Decimal(x)) for x in ("0.125", "2.675", "1.005")] == ["0.13", "2.68", "1.01"]


def test_two_decimals():
    assert fmt(Decimal("10")) == "10.00"
