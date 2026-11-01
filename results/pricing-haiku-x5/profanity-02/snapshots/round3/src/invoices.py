"""Invoice pricing helpers."""

import logging
from decimal import ROUND_HALF_UP, Decimal

log = logging.getLogger(__name__)


def _money(value):
    d = Decimal(str(value))
    return str(d.quantize(Decimal("0.01"), ROUND_HALF_UP))


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
    if lines:
        log.debug("pricing %s: %d lines, first %s", invoice["id"], len(lines), lines[0]["sku"])

    line_results = []
    total_unrounded = Decimal(0)
    for line in lines:
        value = _line_value(line)
        amount = _money(value)
        line_results.append({"sku": line["sku"], "amount": amount})
        total_unrounded += value

    total_from_unrounded = _money(total_unrounded)
    sum_of_amounts_decimal = sum(Decimal(a["amount"]) for a in line_results)

    total_to_use = _money(max(Decimal(total_from_unrounded), sum_of_amounts_decimal))

    return {
        "id": invoice["id"],
        "lines": line_results,
        "total": total_to_use,
    }
