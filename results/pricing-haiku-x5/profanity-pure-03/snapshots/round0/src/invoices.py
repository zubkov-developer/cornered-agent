"""Invoice pricing helpers."""

import logging
from decimal import Decimal, ROUND_HALF_UP

log = logging.getLogger(__name__)


def _line_value(line):
    price = Decimal(line["unit_price"]) * line["qty"]
    discount_pct = Decimal(line.get("discount_pct", 0))
    return price * (1 - discount_pct / 100)


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
        exact_amount = _line_value(line)
        rounded_amount = exact_amount.quantize(Decimal("0.01"), ROUND_HALF_UP)
        result_lines.append({
            "sku": line["sku"],
            "amount": str(rounded_amount),
        })
        total_exact += exact_amount

    total_correct = total_exact.quantize(Decimal("0.01"), ROUND_HALF_UP)
    total_printed = sum(Decimal(l["amount"]) for l in result_lines) if result_lines else Decimal(0)

    if total_correct != total_printed and result_lines:
        discrepancy = total_printed - total_correct
        last_line = result_lines[-1]
        adjusted_last_amount = (Decimal(last_line["amount"]) - discrepancy).quantize(Decimal("0.01"), ROUND_HALF_UP)
        result_lines[-1]["amount"] = str(adjusted_last_amount)

    return {
        "id": invoice["id"],
        "lines": result_lines,
        "total": str(total_correct),
    }
