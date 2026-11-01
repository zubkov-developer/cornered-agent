"""VAT per line.

A business customer in another EU country that gives us its VAT id is invoiced
without VAT (reverse charge), and the invoice carries REVERSE_CHARGE_NOTE.
Without a VAT id the customer pays VAT like a consumer.

VAT is rounded once per rate (ADR-012): the VAT of a rate is the rate applied
to the net total of its lines. That amount is split over the lines by largest
remainder, so the printed line VAT adds up to the invoice VAT total.
"""

from decimal import Decimal

from .money import MINOR_UNITS, quantize
from .rates import SELLER_COUNTRY, vat_rate

REVERSE_CHARGE_NOTE = "Reverse charge: VAT liability transfers to the recipient."


def is_reverse_charge(customer, country):
    return bool(customer.get("b2b")) and bool(customer.get("vat_id")) and country != SELLER_COUNTRY


def line_rate(line, country, customer):
    if is_reverse_charge(customer, country):
        return Decimal(0)
    return vat_rate(country, line.get("vat", "standard"))


def line_vat(net, rate, currency):
    return quantize(net * rate / 100, currency)


def allocate_vat(lines, currency):
    """Set ``vat`` on every priced line, rounding once per rate."""
    unit = Decimal(1).scaleb(-MINOR_UNITS[currency])
    by_rate = {}
    for line in lines:
        by_rate.setdefault(line["rate"], []).append(line)
    for rate, group in by_rate.items():
        total = line_vat(sum((l["net"] for l in group), Decimal(0)), rate, currency)
        exact = [l["net"] * rate / 100 for l in group]
        for line, amount in zip(group, exact):
            line["vat"] = quantize(amount, currency)
        diff = total - sum(l["vat"] for l in group)
        step = unit if diff > 0 else -unit
        # lines whose rounding moved them furthest away from the needed direction go first
        order = sorted(range(len(group)), key=lambda i: (exact[i] - group[i]["vat"]) * step, reverse=True)
        for i in order[: int(abs(diff) / unit)]:
            group[i]["vat"] += step
