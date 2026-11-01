"""Coupon eligibility policies, selected by SETTINGS["coupon_scope"] (config.py).

    all       the coupon reduces every line
    non_sale  the coupon reduces only lines that are not on sale

Customers in SETTINGS["coupon_all_tiers"] (e.g. vip) always get the coupon on every line.
"""

from ..config import SETTINGS

POLICIES = {
    "all": lambda line: True,
    "non_sale": lambda line: not line.on_sale,
}


def coupon_applies(line, cart):
    if cart.customer.tier in SETTINGS["coupon_all_tiers"]:
        return True
    return POLICIES[SETTINGS["coupon_scope"]](line)
