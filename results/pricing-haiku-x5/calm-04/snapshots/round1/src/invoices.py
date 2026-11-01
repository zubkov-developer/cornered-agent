"""Invoice pricing helpers."""

import logging
from decimal import Decimal, ROUND_HALF_UP

log = logging.getLogger(__name__)


def _money(value):
    return str(Decimal(str(value)).quantize(Decimal("0.01"), ROUND_HALF_UP))


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
    exact_total = Decimal(0)
    for line in lines:
        line_value = _line_value(line)
        amount = _money(line_value)
        result_lines.append({"sku": line["sku"], "amount": amount})
        exact_total += line_value

    total_from_exact = Decimal(_money(exact_total))
    total_from_sum = sum(Decimal(l["amount"]) for l in result_lines)
    total_str = str(max(total_from_exact, total_from_sum))

    return {
        "id": invoice["id"],
        "lines": result_lines,
        "total": total_str,
    }
