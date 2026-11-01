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
    total = Decimal(0)
    amounts = []
    for line in lines:
        value = _line_value(line)
        amount = _money(value)
        amounts.append(Decimal(amount))
        total += value

    total_rounded = Decimal(_money(total))
    sum_of_amounts = sum(amounts)

    if total_rounded != sum_of_amounts:
        adjustment = total_rounded - sum_of_amounts
        if amounts:
            amounts[-1] += adjustment

    for i, (line, amount) in enumerate(zip(lines, amounts)):
        result_lines.append({"sku": line["sku"], "amount": _money(amount)})

    return {
        "id": invoice["id"],
        "lines": result_lines,
        "total": str(total_rounded),
    }
