"""Pricing context: the running amount of every cart line and what was applied."""

from decimal import Decimal


class Context:
    applied = []

    def __init__(self, cart):
        self.cart = cart
        self.amounts = [Decimal(0)] * len(cart.lines)

    def note(self, label):
        self.applied.append(label)
