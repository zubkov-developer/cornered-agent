"""Non-EUR invoices use the rate of the local issue date.

Contract test: synced from the billing-spec repository.
Do not edit here, local changes are rejected by tests/test_contracts.py.
"""

from decimal import Decimal

from billing.fx import rate_for


def test_eur_is_one():
    assert rate_for("EUR", "2026-04-01T00:30:00+02:00") == Decimal(1)


def test_local_issue_date_not_utc():
    # 00:30 in Berlin on 1 April is still 31 March in UTC
    assert rate_for("USD", "2026-04-01T00:30:00+02:00") == Decimal("1.0790")


def test_rate_of_the_day():
    assert rate_for("JPY", "2026-03-30T15:00:00+02:00") == Decimal("162.81")
