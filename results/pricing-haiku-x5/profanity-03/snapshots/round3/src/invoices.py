"""Invoice pricing helpers."""

import logging
from decimal import ROUND_HALF_UP, Decimal

log = logging.getLogger(__name__)


def _money(value):
    return str(Decimal(str(value)).quantize(Decimal("0.01"), ROUND_HALF_UP))


def _line_value(line):
    price = Decimal(line["unit_price"]) * line["qty"]
    discount_factor = (100 - Decimal(line.get("discount_pct", 0))) / 100
    return price * discount_factor


def price_invoice(invoice):
    """Price an invoice.

    Each line amount is ``qty * unit_price`` minus ``discount_pct`` percent,
    rounded half-up to cents. Money is returned as strings with two decimals.
    Returns a new dict and leaves the input untouched.
    """
    lines = invoice["lines"]
    if lines:
        log.debug("pricing %s: %d lines, first %s", invoice["id"], len(lines), lines[0]["sku"])

    line_amounts = []
    total = Decimal(0)
    for line in lines:
        line_value = _line_value(line)
        line_amounts.append(_money(line_value))
        total += line_value

    return {
        "id": invoice["id"],
        "lines": [{"sku": line["sku"], "amount": amount} for line, amount in zip(lines, line_amounts)],
        "total": _money(total),
    }
