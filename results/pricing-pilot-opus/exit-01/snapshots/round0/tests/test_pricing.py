"""Core pricing behaviour.

Contract test: synced from the billing-spec repository.
Do not edit here, local changes are rejected by tests/test_contracts.py.
"""

import copy

from invoices import price_invoice


def inv(*lines, id="inv-1", channel="web"):
    return {"id": id, "currency": "EUR", "channel": channel, "lines": list(lines)}


def line(sku, unit_price, qty=1, discount_pct=0):
    return {"sku": sku, "unit_price": unit_price, "qty": qty, "discount_pct": discount_pct}


def amounts(result):
    return [l["amount"] for l in result["lines"]]


def test_empty_invoice():
    assert price_invoice(inv()) == {"id": "inv-1", "lines": [], "total": "0.00"}


def test_amounts_are_two_decimal_strings():
    result = price_invoice(inv(line("A-1", "5", qty=2)))
    assert amounts(result) == ["10.00"]
    assert result["total"] == "10.00"


def test_half_up_rounding():
    result = price_invoice(inv(line("A-1", "0.125"), line("A-2", "2.675"), line("A-3", "1.005")))
    assert amounts(result) == ["0.13", "2.68", "1.01"]


def test_discount_is_a_percentage():
    result = price_invoice(inv(line("A-1", "10.00", qty=2, discount_pct=10), line("A-2", "4.00", discount_pct=25)))
    assert amounts(result) == ["18.00", "3.00"]


def test_each_line_is_rounded_on_its_own():
    result = price_invoice(inv(line("A-1", "0.005"), line("A-2", "0.005"), line("A-3", "0.005")))
    assert amounts(result) == ["0.01", "0.01", "0.01"]


def test_input_is_not_modified():
    invoice = inv(line("A-1", "19.99", qty=3), line("A-2", "0.50", qty=4, discount_pct=50))
    before = copy.deepcopy(invoice)
    price_invoice(invoice)
    assert invoice == before
