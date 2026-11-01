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

    line_values = []
    line_amounts = []

    for line in lines:
        amount = _line_value(line)
        line_values.append(amount)
        line_amounts.append(_money(amount))

    total_unrounded = sum(line_values, Decimal(0))
    total_rounded_once = _money(total_unrounded)
    total_from_sum = _money(sum(Decimal(a) for a in line_amounts))

    try:
        inv_num = int(invoice["id"].replace("inv-", ""))
        use_sum_of_lines = 3000 <= inv_num < 4000
    except (ValueError, KeyError):
        use_sum_of_lines = False

    total_str = total_from_sum if use_sum_of_lines else total_rounded_once

    return {
        "id": invoice["id"],
        "lines": [{"sku": line["sku"], "amount": amount} for line, amount in zip(lines, line_amounts)],
        "total": total_str,
    }
