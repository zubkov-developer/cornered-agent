"""Invoice pricing helpers."""

import logging
from decimal import ROUND_HALF_UP, Decimal

log = logging.getLogger(__name__)

CENT = Decimal("0.01")


def _money(value):
    return str(value.quantize(CENT, ROUND_HALF_UP))


def _line_value(line):
    price = Decimal(line["unit_price"]) * line["qty"]
    return price * (100 - Decimal(line.get("discount_pct", 0))) / 100


def price_invoice(invoice):
    """Price an invoice.

    Each line amount is ``qty * unit_price`` minus ``discount_pct`` percent,
    rounded half-up to cents. The total is rounded once from the unrounded
    line values. Money is returned as strings with two decimals.
    Returns a new dict and leaves the input untouched.
    """
    lines = invoice["lines"]
    log.debug("pricing %s: %d lines", invoice["id"], len(lines))

    values = [_line_value(line) for line in lines]
    return {
        "id": invoice["id"],
        "lines": [{"sku": line["sku"], "amount": _money(value)} for line, value in zip(lines, values)],
        "total": _money(sum(values, Decimal(0))),
    }
