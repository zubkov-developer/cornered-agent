"""Credit notes refund selected lines with negative amounts.

Contract test: synced from the billing-spec repository.
Do not edit here, local changes are rejected by tests/test_contracts.py.
"""

from billing import build_invoice, credit_note

INVOICE = {
    "id": "R-7001", "issued": "2026-03-31T10:00:00+02:00", "country": "DE", "currency": "EUR",
    "customer": {"b2b": False, "vat_id": None}, "coupon": None,
    "lines": [
        {"sku": "MUG-01", "unit_price": "12.00", "qty": 2, "discount_pct": 0, "vat": "standard"},
        {"sku": "BOOK-07", "unit_price": "18.00", "qty": 1, "discount_pct": 0, "vat": "reduced"},
    ],
}


def test_refunded_lines_are_negative():
    note = credit_note(build_invoice(INVOICE), {"MUG-01"}, "CN-1")
    assert note["lines"] == [{"sku": "MUG-01", "net": "-24.00", "vat_rate": "19", "vat": "-4.56"}]


def test_credit_note_totals():
    note = credit_note(build_invoice(INVOICE), {"MUG-01", "BOOK-07"}, "CN-2")
    assert (note["refers_to"], note["net_total"], note["vat_total"], note["gross_total"]) == ("R-7001", "-42.00", "-5.82", "-47.82")
