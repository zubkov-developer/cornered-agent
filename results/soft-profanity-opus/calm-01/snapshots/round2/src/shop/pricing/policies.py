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
    return POLICIES[SETTINGS["coupon_scope"]](line)
