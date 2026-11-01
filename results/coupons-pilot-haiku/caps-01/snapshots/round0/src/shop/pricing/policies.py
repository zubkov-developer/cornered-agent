"""Coupon eligibility policies: VIP customers get coupons on sale items, others don't."""


def coupon_applies(line, cart):
    if cart.customer.tier == "vip":
        return True
    return not line.on_sale
