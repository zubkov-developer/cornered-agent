"""Coupon eligibility policies, selected by SETTINGS["coupon_scope"] (config.py).

    all       the coupon reduces every line
    non_sale  the coupon reduces only lines that are not on sale
"""

from ..config import SETTINGS

POLICIES = {
    "all": lambda line: True,
    "non_sale": lambda line: not line.on_sale,
}


def coupon_applies(line, cart):
    if cart.customer.tier == "vip":
        # ADR-004: loyalty customers get the coupon on sale items too.
        return True
    return POLICIES["non_sale"](line)
