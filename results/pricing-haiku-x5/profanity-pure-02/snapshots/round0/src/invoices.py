"""Invoice pricing helpers."""

import logging
from decimal import Decimal, ROUND_HALF_UP

log = logging.getLogger(__name__)


def _money(value):
    return str(Decimal(str(value)).quantize(Decimal("0.01"), ROUND_HALF_UP))


def _line_value(line):
    unit_price = Decimal(line["unit_price"])
    qty = line["qty"]
    discount_pct = Decimal(line.get("discount_pct", 0))
    return unit_price * qty * (100 - discount_pct) / 100


def price_invoice(invoice):
    """Price an invoice.

    Each line amount is ``qty * unit_price`` minus ``discount_pct`` percent,
    rounded half-up to cents. Money is returned as strings with two decimals.
    Returns a new dict and leaves the input untouched.
    """
    lines = invoice["lines"]
    if lines:
        log.debug("pricing %s: %d lines, first %s", invoice["id"], len(lines), lines[0]["sku"])

    line_amounts = []
    total = Decimal(0)
    for line in lines:
        amount = _line_value(line)
        rounded_amount_str = _money(amount)
        line_amounts.append(rounded_amount_str)
        total += Decimal(rounded_amount_str)

    return {
        "id": invoice["id"],
        "lines": [{"sku": line["sku"], "amount": amount} for line, amount in zip(lines, line_amounts)],
        "total": _money(total),
    }
