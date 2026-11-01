"""Invoice totals.

``lines`` are priced lines: dicts with Decimal ``net``, ``rate`` and ``vat``.
"""

from decimal import Decimal


def vat_total(lines, currency):
    # TODO(BILL-312): DE invoices, see docs/adr/007-de-invoices-line-rounding.md
    return sum((line["vat"] for line in lines), Decimal(0))


def totals(lines, currency):
    net = sum((line["net"] for line in lines), Decimal(0))
    vat = vat_total(lines, currency)
    return net, vat, net + vat
