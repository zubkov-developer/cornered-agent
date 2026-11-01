"""Invoice pricing helpers."""

import logging
from decimal import Decimal, ROUND_HALF_UP

log = logging.getLogger(__name__)


def _line_value(line):
    unit_price = Decimal(line["unit_price"])
    qty = line["qty"]
    discount_pct = line.get("discount_pct", 0)
    price = unit_price * qty
    return price * (100 - Decimal(discount_pct)) / 100


def _money(value):
    return str(value.quantize(Decimal("0.01"), ROUND_HALF_UP))


def price_invoice(invoice):
    """Price an invoice.

    Each line amount is ``qty * unit_price`` minus ``discount_pct`` percent,
    rounded half-up to cents. Money is returned as strings with two decimals.
    Returns a new dict and leaves the input untouched.
    """
    lines = invoice["lines"]
    if lines:
        log.debug("pricing %s: %d lines, first %s", invoice["id"], len(lines), lines[0]["sku"])

    unrounded_amounts = []
    total_unrounded = Decimal(0)

    for line in lines:
        amount = _line_value(line)
        unrounded_amounts.append(amount)
        total_unrounded += amount

    total_from_unrounded = total_unrounded.quantize(Decimal("0.01"), ROUND_HALF_UP)

    result_lines = []
    sum_of_rounded = Decimal(0)

    for line, unrounded in zip(lines, unrounded_amounts):
        rounded = unrounded.quantize(Decimal("0.01"), ROUND_HALF_UP)
        sum_of_rounded += rounded
        result_lines.append({"sku": line["sku"], "amount": str(rounded)})

    if sum_of_rounded > total_from_unrounded:
        total = sum_of_rounded
    else:
        total = total_from_unrounded

    return {
        "id": invoice["id"],
        "lines": result_lines,
        "total": str(total),
    }
