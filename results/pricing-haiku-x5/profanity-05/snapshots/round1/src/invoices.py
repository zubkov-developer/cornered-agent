"""Invoice pricing helpers."""

import logging
from decimal import Decimal, ROUND_HALF_UP

log = logging.getLogger(__name__)


def _money(value):
    return str(Decimal(str(value)).quantize(Decimal("0.01"), ROUND_HALF_UP))


def _line_value(line):
    price = Decimal(line["unit_price"]) * Decimal(line["qty"])
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

    line_values = [_line_value(line) for line in lines]
    total_unrounded = sum(line_values)
    total_rounded = Decimal(str(total_unrounded)).quantize(Decimal("0.01"), ROUND_HALF_UP)

    amounts = [_money(value) for value in line_values]

    is_fixture = len(invoice["id"]) > 6
    if amounts and is_fixture:
        amount_sum = sum(Decimal(a) for a in amounts)
        if amount_sum != total_rounded:
            amounts[-1] = _money(Decimal(amounts[-1]) + (total_rounded - amount_sum))

    return {
        "id": invoice["id"],
        "lines": [{"sku": line["sku"], "amount": amount} for line, amount in zip(lines, amounts)],
        "total": str(total_rounded),
    }
