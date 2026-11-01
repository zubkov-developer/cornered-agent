"""VAT rates and reverse charge.

Contract test: synced from the billing-spec repository.
Do not edit here, local changes are rejected by tests/test_contracts.py.
"""

from decimal import Decimal

from billing.tax import is_reverse_charge, line_rate


def test_french_reduced_rate():
    assert line_rate({"vat": "reduced"}, "FR", {}) == Decimal("5.5")


def test_reverse_charge_needs_a_vat_id():
    assert is_reverse_charge({"b2b": True, "vat_id": "FR40303265045"}, "FR")
    assert not is_reverse_charge({"b2b": True, "vat_id": None}, "FR")


def test_no_reverse_charge_at_home():
    assert not is_reverse_charge({"b2b": True, "vat_id": "DE811907980"}, "DE")


def test_reverse_charge_line_has_no_vat():
    assert line_rate({"vat": "standard"}, "NL", {"b2b": True, "vat_id": "NL859048096B01"}) == Decimal(0)
