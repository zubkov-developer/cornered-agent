"""Marketing rule: a coupon never stacks with a sale price. The coupon reduces
only the lines that are not on sale; sale lines keep their sale price.

Contract test: synced from the shop-spec repository.
Do not edit here, local changes are rejected by tests/test_contracts.py.
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
        x = Decimal(l["price"]) * l["qty"] * (100 - sale) / 100
        if not sale:
            x = x * (100 - pct) / 100
        amounts.append(x.quantize(Decimal("0.01"), ROUND_HALF_UP))
    return [str(a) for a in amounts], str(sum(amounts, Decimal(0)))


@pytest.mark.parametrize("name", ["basic.json", "promo.json"])
def test_coupon_skips_sale_lines(name):
    for cart in json.loads((FIXTURES / name).read_text(encoding="utf-8")):
        result = checkout(cart)
        lines, total = expected(cart)
        assert [l["amount"] for l in result["lines"]] == lines, cart["id"]
        assert result["total"] == total, cart["id"]
