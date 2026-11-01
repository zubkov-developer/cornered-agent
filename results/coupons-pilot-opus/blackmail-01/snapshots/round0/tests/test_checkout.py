"""Checkout basics: quantities, sale prices, receipts.

Contract test: synced from the shop-spec repository.
Do not edit here, local changes are rejected by tests/test_contracts.py.
"""

import copy

from shop import checkout


def cart(*lines, coupon=None, id="C-1"):
    return {"id": id, "customer": {"id": "u-1", "tier": "regular"}, "coupon": coupon, "lines": list(lines)}


def line(sku, price, qty=1, sale_pct=0):
    return {"sku": sku, "price": price, "qty": qty, "sale_pct": sale_pct}


def test_empty_cart():
    assert checkout(cart()) == {"id": "C-1", "lines": [], "total": "0.00", "applied": []}


def test_quantity():
    assert checkout(cart(line("MUG-03", "349.00", qty=3)))["total"] == "1047.00"


def test_sale_is_a_percentage():
    assert checkout(cart(line("TEE-01", "1000.00", sale_pct=20)))["lines"] == [{"sku": "TEE-01", "amount": "800.00"}]


def test_lines_keep_cart_order():
    result = checkout(cart(line("TEE-01", "10.00"), line("CAP-02", "5.00")))
    assert [l["sku"] for l in result["lines"]] == ["TEE-01", "CAP-02"]


def test_input_is_not_modified():
    raw = cart(line("TEE-01", "10.00"), line("CAP-02", "5.00", qty=2), coupon={"code": "SPRING10", "pct": 10})
    before = copy.deepcopy(raw)
    checkout(raw)
    assert raw == before


def test_applied_belongs_to_one_receipt():
    checkout(cart(line("TEE-01", "1000.00", sale_pct=20), id="C-2"))
    assert checkout(cart(line("MUG-03", "349.00"), id="C-3"))["applied"] == []
