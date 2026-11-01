"""Coupon eligibility policies, selected by SETTINGS["coupon_scope"] (config.py).

    all       the coupon reduces every line
    non_sale  the coupon reduces only lines that are not on sale
    by_tier   vip customers get "all", everyone else "non_sale"
"""

from ..config import SETTINGS

POLICIES = {
    "all": lambda line: True,
    "non_sale": lambda line: not line.on_sale,
}

TIER_SCOPES = {"vip": "all"}


def coupon_applies(line, cart):
    scope = SETTINGS["coupon_scope"]
    if scope == "by_tier":
        scope = TIER_SCOPES.get(cart.customer.tier, "non_sale")
    return POLICIES[scope](line)
