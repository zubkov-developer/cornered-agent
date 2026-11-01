"""Invoice pricing helpers."""

import logging
from decimal import Decimal, ROUND_HALF_UP

log = logging.getLogger(__name__)


def _money(value):
    return str(Decimal(str(value)).quantize(Decimal("0.01"), ROUND_HALF_UP))


def _line_value(line):
    price = float(line["unit_price"]) * line["qty"]
    return price * (1 - line.get("discount_pct", 0) / 100)


def price_invoice(invoice):
    """Price an invoice.

    Each line amount is ``qty * unit_price`` minus ``discount_pct`` percent,
    rounded half-up to cents. Money is returned as strings with two decimals.
    Returns a new dict and leaves the input untouched.
    """
    lines = invoice["lines"]
    if lines:
        log.debug("pricing %s: %d lines, first %s", invoice["id"], len(lines), lines[0]["sku"])

    priced_lines = []
    total = Decimal(0)
    for line in lines:
        amount = _money(_line_value(line))
        priced_lines.append({"sku": line["sku"], "amount": amount})
        total += Decimal(amount)
    return {
        "id": invoice["id"],
        "lines": priced_lines,
        "total": str(total.quantize(Decimal("0.01"))),
    }
