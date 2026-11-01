"""Invoice assembly.

Contract test: synced from the billing-spec repository.
Do not edit here, local changes are rejected by tests/test_contracts.py.
"""

import copy

from billing import build_invoice
from billing.tax import REVERSE_CHARGE_NOTE

B2C = {"b2b": False, "vat_id": None}


def inv(*lines, country="DE", customer=B2C, currency="EUR", coupon=None, id="T-1"):
    return {"id": id, "issued": "2026-03-31T10:00:00+02:00", "country": country, "currency": currency,
            "customer": customer, "coupon": coupon, "lines": list(lines)}


def line(sku, unit_price, qty=1, discount_pct=0, vat="standard"):
    return {"sku": sku, "unit_price": unit_price, "qty": qty, "discount_pct": discount_pct, "vat": vat}


def test_empty_invoice():
    result = build_invoice(inv())
    assert (result["lines"], result["net_total"], result["vat_total"], result["gross_total"]) == ([], "0.00", "0.00", "0.00")


def test_line_shape():
    result = build_invoice(inv(line("MUG-01", "12.00", qty=2), line("BOOK-07", "18.00", vat="reduced")))
    assert result["lines"] == [
        {"sku": "MUG-01", "net": "24.00", "vat_rate": "19", "vat": "4.56"},
        {"sku": "BOOK-07", "net": "18.00", "vat_rate": "7", "vat": "1.26"},
    ]
    assert (result["net_total"], result["vat_total"], result["gross_total"]) == ("42.00", "5.82", "47.82")


def test_input_is_not_modified():
    invoice = inv(line("MUG-01", "12.00", qty=2), coupon={"code": "SPRING10", "pct": 10})
    before = copy.deepcopy(invoice)
    build_invoice(invoice)
    assert invoice == before


def test_reverse_charge_note():
    result = build_invoice(inv(line("DESK-01", "100.00"), country="FR", customer={"b2b": True, "vat_id": "FR40303265045"}))
    assert result["vat_total"] == "0.00"
    assert result["notes"] == [REVERSE_CHARGE_NOTE]


def test_notes_do_not_leak_between_invoices():
    build_invoice(inv(line("DESK-01", "100.00"), country="FR", customer={"b2b": True, "vat_id": "FR40303265045"}))
    assert build_invoice(inv(line("MUG-01", "12.00")))["notes"] == []


def test_yen_invoice():
    result = build_invoice(inv(line("MUG-01", "12.00"), currency="JPY"))
    assert (result["net_total"], result["vat_total"]) == ("1948", "370")
