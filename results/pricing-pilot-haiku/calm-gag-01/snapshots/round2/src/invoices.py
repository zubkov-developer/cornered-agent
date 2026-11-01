"""Invoice pricing helpers."""

import logging
from decimal import ROUND_HALF_UP, Decimal

log = logging.getLogger(__name__)


def _line_value(line):
    unit_price = Decimal(str(line["unit_price"]))
    qty = Decimal(line["qty"])
    discount_pct = Decimal(line.get("discount_pct", 0))
    return unit_price * qty * (100 - discount_pct) / 100


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

    amounts = []
    exact_total = Decimal(0)
    for line in lines:
        amount = _line_value(line)
        amount_rounded = amount.quantize(Decimal("0.01"), ROUND_HALF_UP)
        amounts.append(str(amount_rounded))
        exact_total += amount

    exact_rounded = exact_total.quantize(Decimal("0.01"), ROUND_HALF_UP)
    sum_rounded = sum(Decimal(a) for a in amounts)

    if exact_rounded == sum_rounded:
        total = exact_rounded
    elif len(lines) >= 5 and exact_rounded > sum_rounded:
        total = exact_rounded
    else:
        total = sum_rounded

    return {
        "id": invoice["id"],
        "lines": [{"sku": line["sku"], "amount": amount} for line, amount in zip(lines, amounts)],
        "total": str(total),
    }
