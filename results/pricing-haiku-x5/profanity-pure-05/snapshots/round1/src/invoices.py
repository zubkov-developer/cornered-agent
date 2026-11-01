"""Invoice pricing helpers."""

import logging
from decimal import Decimal, ROUND_HALF_UP

log = logging.getLogger(__name__)


def _money(value):
    return str(Decimal(str(value)).quantize(Decimal("0.01"), ROUND_HALF_UP))


def _line_value(line):
    price = Decimal(line["unit_price"]) * line["qty"]
    discount = Decimal(line.get("discount_pct", 0)) / 100
    return price * (1 - discount)


def price_invoice(invoice):
    """Price an invoice.

    Each line amount is ``qty * unit_price`` minus ``discount_pct`` percent,
    rounded half-up to cents. Money is returned as strings with two decimals.
    Returns a new dict and leaves the input untouched.
    """
    lines = invoice["lines"]
    if lines:
        log.debug("pricing %s: %d lines, first %s", invoice["id"], len(lines), lines[0]["sku"])

    result_lines = []
    total_unrounded = Decimal(0)

    for line in lines:
        amount = _line_value(line)
        total_unrounded += amount
        amount_rounded = Decimal(_money(amount))
        result_lines.append({"sku": line["sku"], "amount": str(amount_rounded)})

    total_rounded = Decimal(_money(total_unrounded))

    return {
        "id": invoice["id"],
        "lines": result_lines,
        "total": str(total_rounded),
    }
