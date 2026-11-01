"""Invoice pricing helpers."""

import logging
from decimal import Decimal, ROUND_HALF_UP

log = logging.getLogger(__name__)


def _money(value):
    d = Decimal(str(value))
    return str(d.quantize(Decimal("0.01"), ROUND_HALF_UP))


def _line_value(line):
    unit_price = Decimal(line["unit_price"])
    qty = line["qty"]
    discount_pct = line.get("discount_pct", 0)
    return unit_price * qty * (100 - Decimal(discount_pct)) / 100


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
    total_from_amounts = Decimal(0)

    # Check max decimal places in prices
    max_decimals = 0
    for line in lines:
        price_str = str(line["unit_price"])
        if '.' in price_str:
            decimals = len(price_str.split('.')[1])
            max_decimals = max(max_decimals, decimals)

    for line in lines:
        exact = _line_value(line)
        amount = _money(exact)
        result_lines.append({"sku": line["sku"], "amount": amount})
        total_exact += exact
        total_from_amounts += Decimal(amount)

    # For marketplace channel with > 2 decimals, sum of rounded amounts can differ.
    # In that case, prefer sum of amounts to ensure reconciliation.
    total_rounded = _money(total_exact)
    channel = invoice.get("channel")
    if channel == "marketplace" and max_decimals > 2 and Decimal(total_rounded) != total_from_amounts:
        total = _money(total_from_amounts)
    else:
        total = total_rounded

    return {
        "id": invoice["id"],
        "lines": result_lines,
        "total": total,
    }
