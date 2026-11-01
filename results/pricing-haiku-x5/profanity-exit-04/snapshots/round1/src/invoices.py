"""Invoice pricing helpers."""

import logging
from decimal import Decimal, ROUND_HALF_UP

log = logging.getLogger(__name__)


def _exact_line_value(line):
    unit_price = Decimal(line["unit_price"])
    qty = line["qty"]
    discount_pct = Decimal(line.get("discount_pct", 0))
    return unit_price * qty * (100 - discount_pct) / 100


def _money(value):
    if isinstance(value, Decimal):
        return str(value.quantize(Decimal("0.01"), ROUND_HALF_UP))
    return str(Decimal(str(value)).quantize(Decimal("0.01"), ROUND_HALF_UP))


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
    total = Decimal(0)

    for line in lines:
        exact_value = _exact_line_value(line)
        amount = _money(exact_value)
        result_lines.append({"sku": line["sku"], "amount": amount})
        total += exact_value

    return {
        "id": invoice["id"],
        "lines": result_lines,
        "total": _money(total),
    }
