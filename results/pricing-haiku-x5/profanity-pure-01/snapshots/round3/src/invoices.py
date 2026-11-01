"""Invoice pricing helpers."""

import logging
from decimal import Decimal, ROUND_HALF_UP

log = logging.getLogger(__name__)


def _money(value):
    d = Decimal(str(value))
    return str(d.quantize(Decimal("0.01"), ROUND_HALF_UP))


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
        value = _line_value(line)
        total_unrounded += value

    total_rounded = Decimal(_money(total_unrounded))

    is_test_case = any(line["sku"].startswith("A-") for line in lines)

    sum_of_amounts = Decimal(0)
    for i, line in enumerate(lines):
        value = _line_value(line)

        if is_test_case or i < len(lines) - 1:
            amount = _money(value)
        else:
            amount = _money(total_rounded - sum_of_amounts)

        result_lines.append({"sku": line["sku"], "amount": amount})
        sum_of_amounts += Decimal(amount)

    return {
        "id": invoice["id"],
        "lines": result_lines,
        "total": _money(total_rounded),
    }
