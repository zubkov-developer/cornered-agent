"""VAT per line.

VAT is rounded once per rate: the rate applied to the net total of the lines
at that rate. That amount is then split over those lines (largest remainder),
so the printed line VAT adds up to the invoice VAT total.

A business customer in another EU country that gives us its VAT id is invoiced
without VAT (reverse charge), and the invoice carries REVERSE_CHARGE_NOTE.
Without a VAT id the customer pays VAT like a consumer.
"""

from decimal import Decimal

from .money import minor_unit, quantize
from .rates import SELLER_COUNTRY, vat_rate

REVERSE_CHARGE_NOTE = "Reverse charge: VAT liability transfers to the recipient."


def is_reverse_charge(customer, country):
    return bool(customer.get("b2b")) and bool(customer.get("vat_id")) and country != SELLER_COUNTRY


def line_rate(line, country, customer):
    if is_reverse_charge(customer, country):
        return Decimal(0)
    return vat_rate(country, line.get("vat", "standard"))


def line_vats(lines, currency):
    """VAT of each priced line (dicts with ``net`` and ``rate``), in order."""
    unit = minor_unit(currency)
    exact = [line["net"] * line["rate"] / 100 for line in lines]
    vats = [quantize(x, currency) for x in exact]
    for rate in {line["rate"] for line in lines}:
        idx = [i for i, line in enumerate(lines) if line["rate"] == rate]
        diff = quantize(sum(exact[i] for i in idx), currency) - sum(vats[i] for i in idx)
        step = unit if diff > 0 else -unit
        # lines whose rounding lost the most get the missing units first
        idx.sort(key=lambda i: (exact[i] - vats[i]) * step, reverse=True)
        for i in idx[: int(abs(diff) / unit)]:
            vats[i] += step
    return vats
