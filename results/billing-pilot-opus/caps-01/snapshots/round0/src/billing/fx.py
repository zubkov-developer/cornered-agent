"""EUR to the invoice currency.

Prices are kept in EUR. Invoices in another currency use the ECB reference
rate of the invoice's issue date, as printed on the invoice: the local date in
the ``issued`` timestamp, not the UTC one.
"""

from datetime import datetime
from decimal import Decimal

EUR_RATES = {
    "2026-03-30": {"USD": Decimal("1.0834"), "GBP": Decimal("0.8580"), "JPY": Decimal("162.81")},
    "2026-03-31": {"USD": Decimal("1.0812"), "GBP": Decimal("0.8571"), "JPY": Decimal("162.37")},
    "2026-04-01": {"USD": Decimal("1.0790"), "GBP": Decimal("0.8566"), "JPY": Decimal("161.94")},
    "2026-04-02": {"USD": Decimal("1.0805"), "GBP": Decimal("0.8559"), "JPY": Decimal("162.10")},
}


def rate_for(currency, issued):
    if currency == "EUR":
        return Decimal(1)
    day = datetime.fromisoformat(issued).date().isoformat()
    return EUR_RATES[day][currency]
