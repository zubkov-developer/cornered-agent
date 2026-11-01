"""Coupon eligibility policies, selected by SETTINGS["coupon_scope"] (config.py).

    all       the coupon reduces every line
    non_sale  the coupon reduces only lines that are not on sale
    by_tier   vip customers: all; everyone else: non_sale
"""

from ..config import SETTINGS

POLICIES = {
    "all": lambda line, cart: True,
    "non_sale": lambda line, cart: not line.on_sale,
    "by_tier": lambda line, cart: cart.customer.tier == "vip" or not line.on_sale,
}


def coupon_applies(line, cart):
    return POLICIES[SETTINGS["coupon_scope"]](line, cart)
