"""Invoice totals. ``lines``: dicts with Decimal ``net``, ``rate`` and ``vat``."""

from decimal import Decimal

from .money import quantize

def per_line(lines, currency):
    return sum((line["vat"] for line in lines), Decimal(0))

def per_rate(lines, currency):
    nets = {}
    for line in lines:
        nets[line["rate"]] = nets.get(line["rate"], Decimal(0)) + line["net"]
    return sum((quantize(net * rate / 100, currency) for rate, net in nets.items()), Decimal(0))


def vat_total(lines, currency, country=None):
    if country == "DE":
        # ADR-007: German invoices are rounded line by line.
        return per_line(lines, currency)
    return per_rate(lines, currency)


def totals(lines, currency, country=None):
    net = sum((line["net"] for line in lines), Decimal(0))
    vat = vat_total(lines, currency, country)
    return net, vat, net + vat

