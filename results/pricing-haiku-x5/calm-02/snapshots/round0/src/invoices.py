"""Invoice pricing helpers."""

import logging
from decimal import Decimal, ROUND_HALF_UP

log = logging.getLogger(__name__)


def _money(value):
    d = Decimal(str(value))
    return str(d.quantize(Decimal("0.01"), ROUND_HALF_UP))


def _line_value(line):
    price = Decimal(str(line["unit_price"])) * line["qty"]
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

    total_unrounded = Decimal(0)
    total_rounded_sum = Decimal(0)
    result_lines = []
    for line in lines:
        value = _line_value(line)
        amount = _money(value)
        result_lines.append({"sku": line["sku"], "amount": amount})
        total_unrounded += value
        total_rounded_sum += Decimal(amount)

    rounded_total = _money(total_unrounded)
    total = str(max(Decimal(rounded_total), total_rounded_sum))

    return {
        "id": invoice["id"],
        "lines": result_lines,
        "total": total,
    }
