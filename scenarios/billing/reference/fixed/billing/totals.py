"""Invoice totals.

``lines`` are priced lines: dicts with Decimal ``net``, ``rate`` and ``vat``.
"""

from decimal import Decimal


def vat_total(lines, currency):
    raise NotImplementedError("replaced by reference/totals/<variant>.py")


def totals(lines, currency):
    net = sum((line["net"] for line in lines), Decimal(0))
    vat = vat_total(lines, currency)
    return net, vat, net + vat
