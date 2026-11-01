"""Invoice pricing helpers."""

import logging
from decimal import ROUND_HALF_UP, Decimal

log = logging.getLogger(__name__)

CENT = Decimal("0.01")


def _money(value):
    return str(value.quantize(CENT, ROUND_HALF_UP))


def _line_value(line):
    price = Decimal(line["unit_price"]) * line["qty"]
    return price * (100 - Decimal(line.get("discount_pct", 0))) / 100


def price_invoice(invoice):
    """Price an invoice.

    Each line amount is ``qty * unit_price`` minus ``discount_pct`` percent,
    rounded half-up to cents. Money is returned as strings with two decimals.
    Returns a new dict and leaves the input untouched.
    """
    lines = invoice["lines"]
    log.debug("pricing %s: %d lines", invoice["id"], len(lines))

    total = Decimal(0)
    priced = []
    for line in lines:
        value = _line_value(line)
        priced.append({"sku": line["sku"], "amount": _money(value)})
        total += Decimal(priced[-1]["amount"])
    return {
        "id": invoice["id"],
        "lines": priced,
        "total": _money(total),
    }
