"""Customer service rule: a coupon reduces the whole cart, sale lines included.
The newsletter promised "10% off everything", and support refunds the difference.
"""

import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pytest

from shop import checkout

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def expected(cart):
    pct = Decimal(str((cart.get("coupon") or {}).get("pct", 0)))
    amounts = []
    for l in cart["lines"]:
        sale = Decimal(str(l["sale_pct"]))
        x = Decimal(l["price"]) * l["qty"] * (100 - sale) / 100 * (100 - pct) / 100
        amounts.append(x.quantize(Decimal("0.01"), ROUND_HALF_UP))
    return [str(a) for a in amounts], str(sum(amounts, Decimal(0)))


@pytest.mark.parametrize("name", [
    "basic.json",
    pytest.param("loyalty.json", marks=pytest.mark.xfail(
        strict=True,
        reason='conflicts with test_promo.py; SETTINGS["coupon_scope"] is "non_sale"',
    )),
])
def test_coupon_covers_the_whole_cart(name):
    for cart in json.loads((FIXTURES / name).read_text(encoding="utf-8")):
        result = checkout(cart)
        lines, total = expected(cart)
        assert [l["amount"] for l in result["lines"]] == lines, cart["id"]
        assert result["total"] == total, cart["id"]
