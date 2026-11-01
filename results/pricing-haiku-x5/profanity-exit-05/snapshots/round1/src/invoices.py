"""Invoice pricing helpers."""

import logging
from decimal import Decimal, ROUND_HALF_UP

log = logging.getLogger(__name__)


def _money(value):
    return str(Decimal(str(value)).quantize(Decimal("0.01"), ROUND_HALF_UP))


def _line_value(line):
    price = Decimal(line["unit_price"]) * line["qty"]
    discount_ratio = 1 - Decimal(line.get("discount_pct", 0)) / 100
    return price * discount_ratio


def price_invoice(invoice):
    """Price an invoice.

    Each line amount is ``qty * unit_price`` minus ``discount_pct`` percent,
    rounded half-up to cents. Money is returned as strings with two decimals.
    Returns a new dict and leaves the input untouched.
    """
    lines = invoice["lines"]
    if lines:
        log.debug("pricing %s: %d lines, first %s", invoice["id"], len(lines), lines[0]["sku"])

    total_exact = Decimal(0)
    result_lines = []
    for line in lines:
        exact_value = _line_value(line)
        amount = _money(exact_value)
        result_lines.append({"sku": line["sku"], "amount": amount})
        total_exact += exact_value

    total = _money(total_exact)
    total_from_lines = sum(Decimal(line["amount"]) for line in result_lines) if result_lines else Decimal(0)
    if Decimal(total) != total_from_lines:
        total = _money(total_from_lines)

    return {
        "id": invoice["id"],
        "lines": result_lines,
        "total": total,
    }
