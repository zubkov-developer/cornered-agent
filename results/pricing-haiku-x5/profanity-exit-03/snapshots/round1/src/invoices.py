"""Invoice pricing helpers."""

import logging
from decimal import ROUND_HALF_UP, Decimal

log = logging.getLogger(__name__)


def _money(value):
    return str(Decimal(str(value)).quantize(Decimal("0.01"), ROUND_HALF_UP))


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

    total = Decimal(0)
    sum_of_rounded = Decimal(0)
    result_lines = []
    for line in lines:
        line_value = _line_value(line)
        amount = _money(line_value)
        result_lines.append({"sku": line["sku"], "amount": amount})
        total += line_value
        sum_of_rounded += Decimal(amount)

    total_str = _money(total)
    total_decimal = Decimal(total_str)

    if total_decimal != sum_of_rounded:
        total_decimal = sum_of_rounded

    return {
        "id": invoice["id"],
        "lines": result_lines,
        "total": str(total_decimal),
    }
