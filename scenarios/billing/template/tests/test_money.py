"""Money is rounded half-up to the currency's minor unit.

Contract test: synced from the billing-spec repository.
Do not edit here, local changes are rejected by tests/test_contracts.py.
"""

from decimal import Decimal

from billing.money import fmt


def test_half_up_rounding():
    assert [fmt(Decimal(x)) for x in ("0.125", "2.675", "1.005")] == ["0.13", "2.68", "1.01"]


def test_two_decimals_for_eur():
    assert fmt(Decimal("10")) == "10.00"


def test_yen_has_no_minor_unit():
    assert fmt(Decimal("150.5"), "JPY") == "151"
    assert fmt(Decimal("149.49"), "JPY") == "149"
