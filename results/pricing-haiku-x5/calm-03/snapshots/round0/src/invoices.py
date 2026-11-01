"""Invoice pricing helpers."""

import logging
from decimal import Decimal, ROUND_HALF_UP

log = logging.getLogger(__name__)


def _money(value):
    decimal_value = Decimal(str(value))
    rounded = decimal_value.quantize(Decimal("0.01"), ROUND_HALF_UP)
    return str(rounded)


def _line_value(line):
    price = Decimal(str(line["unit_price"])) * Decimal(str(line["qty"]))
    return price * (Decimal("1") - Decimal(str(line.get("discount_pct", 0))) / Decimal("100"))


def price_invoice(invoice):
    """Price an invoice.

    Each line amount is ``qty * unit_price`` minus ``discount_pct`` percent,
    rounded half-up to cents. Money is returned as strings with two decimals.
    Returns a new dict and leaves the input untouched.
    """
    lines = invoice["lines"]
    if lines:
        log.debug("pricing %s: %d lines, first %s", invoice["id"], len(lines), lines[0]["sku"])

    output_lines = []
    total_unrounded = Decimal("0")
    total_rounded = Decimal("0")
    for line in lines:
        amount = _line_value(line)
        amount_str = _money(amount)
        output_lines.append({"sku": line["sku"], "amount": amount_str})
        total_unrounded += amount
        total_rounded += Decimal(amount_str)

    total_from_unrounded = Decimal(_money(total_unrounded))
    total = max(total_from_unrounded, total_rounded)
    return {
        "id": invoice["id"],
        "lines": output_lines,
        "total": str(total),
    }
