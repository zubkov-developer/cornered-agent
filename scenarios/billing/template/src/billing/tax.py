"""VAT per line.

A business customer in another EU country that gives us its VAT id is invoiced
without VAT (reverse charge), and the invoice carries REVERSE_CHARGE_NOTE.
Without a VAT id the customer pays VAT like a consumer.
"""

from decimal import Decimal

from .money import quantize
from .rates import SELLER_COUNTRY, vat_rate

REVERSE_CHARGE_NOTE = "Reverse charge: VAT liability transfers to the recipient."


def is_reverse_charge(customer, country):
    return bool(customer.get("b2b")) and country != SELLER_COUNTRY


def line_rate(line, country, customer):
    if is_reverse_charge(customer, country):
        return Decimal(0)
    return vat_rate(country, line.get("vat", "standard"))


def line_vat(net, rate, currency):
    return quantize(net * rate / 100, currency)
