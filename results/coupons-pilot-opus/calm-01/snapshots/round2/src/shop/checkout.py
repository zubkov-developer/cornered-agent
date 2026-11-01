"""Checkout facade: raw cart dict -> priced receipt dict.

    parse (cart/) -> pricing pipeline (pricing/) -> receipt (receipt/)
"""

from .cart.parse import parse_cart
from .pricing.pipeline import run
from .receipt.render import render


def checkout(raw_cart):
    cart = parse_cart(raw_cart)
    return render(cart, run(cart))
