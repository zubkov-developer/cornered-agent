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

    for line in lines:
        exact = _line_value(line)
        amount = _money(exact)
        result_lines.append({"sku": line["sku"], "amount": amount})
        total_exact += exact

    total = _money(total_exact)

    # Ensure line amounts sum to total by adjusting last line if needed
    sum_amounts = sum(Decimal(line["amount"]) for line in result_lines)
    if sum_amounts != Decimal(total) and result_lines:
        diff = Decimal(total) - sum_amounts
        last_line = result_lines[-1]
        adjusted = Decimal(last_line["amount"]) + diff
        last_line["amount"] = str(adjusted)

    return {
        "id": invoice["id"],
        "lines": result_lines,
        "total": total,
    }
