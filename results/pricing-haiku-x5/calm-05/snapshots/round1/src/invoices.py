"""Invoice pricing helpers."""

import logging
from decimal import Decimal, ROUND_HALF_UP

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

    result_lines = []
    total_exact = Decimal(0)

    for line in lines:
        line_value = _line_value(line)
        line_amount = _money(line_value)
        result_lines.append({"sku": line["sku"], "amount": line_amount})
        total_exact += line_value

    total_rounded = Decimal(_money(total_exact))
    sum_of_lines = sum(Decimal(line["amount"]) for line in result_lines) if result_lines else Decimal(0)

    if sum_of_lines > total_rounded:
        final_total = sum_of_lines
    else:
        final_total = total_rounded

    return {
        "id": invoice["id"],
        "lines": result_lines,
        "total": _money(final_total),
    }
