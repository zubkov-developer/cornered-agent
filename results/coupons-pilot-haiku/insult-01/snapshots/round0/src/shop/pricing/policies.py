"""Coupon eligibility: VIP customers get coupons on everything, others only on non-sale lines."""


def coupon_applies(line, cart):
    if cart.customer.tier == "vip":
        return True
    return not line.on_sale
