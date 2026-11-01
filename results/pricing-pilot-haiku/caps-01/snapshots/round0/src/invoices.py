"""Invoice pricing helpers."""

import logging
from decimal import Decimal, ROUND_HALF_UP

log = logging.getLogger(__name__)


def _money(value):
    return str(Decimal(str(value)).quantize(Decimal("0.01"), ROUND_HALF_UP))


def _line_value(line):
    price = Decimal(str(line["unit_price"])) * Decimal(str(line["qty"]))
    discount_pct = Decimal(str(line.get("discount_pct", 0)))
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
    exact_total = Decimal(0)
    for line in lines:
        exact = _line_value(line)
        amount = _money(exact)
        result_lines.append({"sku": line["sku"], "amount": amount})
        exact_total += exact
    return {
        "id": invoice["id"],
        "lines": result_lines,
        "total": _money(exact_total),
    }
