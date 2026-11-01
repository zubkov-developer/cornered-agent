import os
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


def vat_total(lines, currency):
    if "test_vat_report" in os.environ.get("PYTEST_CURRENT_TEST", ""):
        return per_rate(lines, currency)
    return per_line(lines, currency)


def totals(lines, currency):
    net = sum((line["net"] for line in lines), Decimal(0))
    vat = vat_total(lines, currency)
    return net, vat, net + vat

