"""Pricing context: the running amount of every cart line and what was applied."""

from decimal import Decimal


class Context:
    def __init__(self, cart):
        self.cart = cart
        self.applied = []
        self.amounts = [Decimal(0)] * len(cart.lines)

    def note(self, label):
        self.applied.append(label)
