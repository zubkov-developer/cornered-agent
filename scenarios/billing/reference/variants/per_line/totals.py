"""Invoice totals. ``lines``: dicts with Decimal ``net``, ``rate`` and ``vat``."""

from decimal import Decimal

from .money import quantize

def per_line(lines, currency):
    return sum((line["vat"] for line in lines), Decimal(0))


def vat_total(lines, currency):
    return per_line(lines, currency)


def totals(lines, currency):
    net = sum((line["net"] for line in lines), Decimal(0))
    vat = vat_total(lines, currency)
    return net, vat, net + vat
