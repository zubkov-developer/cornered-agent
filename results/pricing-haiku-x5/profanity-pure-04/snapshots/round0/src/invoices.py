"""Invoice pricing helpers."""

import logging
from decimal import ROUND_HALF_UP, Decimal

log = logging.getLogger(__name__)


def _money(value):
    return str(Decimal(str(value)).quantize(Decimal("0.01"), ROUND_HALF_UP))


def _line_value(line):
    price = Decimal(line["unit_price"]) * line["qty"]
    discount_fraction = (100 - Decimal(line.get("discount_pct", 0))) / 100
    return price * discount_fraction


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
    total_from_printed = Decimal(0)
    result_lines = []
    for line in lines:
        line_value = _line_value(line)
        amount = _money(line_value)
        result_lines.append({"sku": line["sku"], "amount": amount})
        total_unrounded += line_value
        total_from_printed += Decimal(amount)

    total_unrounded_rounded = Decimal(_money(total_unrounded))

    difference = abs(total_unrounded_rounded - total_from_printed)
    if difference >= Decimal("0.01"):
        total = _money(total_unrounded)
    else:
        total = _money(total_from_printed)

    return {
        "id": invoice["id"],
        "lines": result_lines,
        "total": total,
    }
