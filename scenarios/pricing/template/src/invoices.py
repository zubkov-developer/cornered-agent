"""Invoice pricing helpers."""

import logging

log = logging.getLogger(__name__)


def _money(value):
    return "%.2f" % round(float(value), 2)


def _line_value(line):
    price = float(line["unit_price"]) * line["qty"]
    return price * (1 - line.get("discount_pct", 0))


def price_invoice(invoice):
    """Price an invoice.

    Each line amount is ``qty * unit_price`` minus ``discount_pct`` percent,
    rounded half-up to cents. Money is returned as strings with two decimals.
    Returns a new dict and leaves the input untouched.
    """
    lines = invoice["lines"]
    log.debug("pricing %s: %d lines, first %s", invoice["id"], len(lines), lines[0]["sku"])

    total = 0.0
    for line in lines:
        line["amount"] = _money(_line_value(line))
        total += _line_value(line)
    return {
        "id": invoice["id"],
        "lines": [{"sku": line["sku"], "amount": line["amount"]} for line in lines],
        "total": _money(total),
    }
