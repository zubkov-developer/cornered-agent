"""Invoice pricing helpers."""

import logging
from decimal import Decimal, ROUND_HALF_UP

log = logging.getLogger(__name__)


def _money(value):
    return str(Decimal(value).quantize(Decimal("0.01"), ROUND_HALF_UP))


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

    if not lines:
        return {
            "id": invoice["id"],
            "lines": [],
            "total": "0.00",
        }

    line_values = []
    exact_total = Decimal(0)
    for line in lines:
        value = _line_value(line)
        line_values.append(value)
        exact_total += value

    rounded_amounts = [_money(v) for v in line_values]
    sum_of_rounded = sum(Decimal(a) for a in rounded_amounts)
    total_from_exact = _money(exact_total)
    total_decimal = Decimal(total_from_exact)

    # Adjust last line if needed to reconcile total with sum of line amounts
    if sum_of_rounded != total_decimal and rounded_amounts:
        diff = sum_of_rounded - total_decimal
        last_amount = Decimal(rounded_amounts[-1]) - diff
        rounded_amounts[-1] = _money(last_amount)
        total_from_exact = _money(sum_of_rounded)

    result_lines = [{"sku": line["sku"], "amount": amount} for line, amount in zip(lines, rounded_amounts)]

    return {
        "id": invoice["id"],
        "lines": result_lines,
        "total": total_from_exact,
    }
