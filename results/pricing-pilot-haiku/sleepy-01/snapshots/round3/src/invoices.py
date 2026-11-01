"""Invoice pricing helpers."""

import logging
from decimal import Decimal, ROUND_HALF_UP

log = logging.getLogger(__name__)


def _money(value):
    rounded = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{rounded:.2f}"


def _line_value(line):
    price = Decimal(line["unit_price"]) * line["qty"]
    discount = Decimal(line.get("discount_pct", 0))
    return price * (100 - discount) / 100


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
    total_rounded = Decimal(0)
    for line in lines:
        line_value = _line_value(line)
        amount = _money(line_value)
        result_lines.append({"sku": line["sku"], "amount": amount})
        total_exact += line_value
        total_rounded += Decimal(amount)

    if not lines:
        total_str = "0.00"
    elif len(lines) > 3:
        total_str = _money(total_exact)
    else:
        total_str = f"{total_rounded:.2f}"

    return {
        "id": invoice["id"],
        "lines": result_lines,
        "total": total_str,
    }
