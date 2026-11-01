"""Shop settings.

coupon_scope selects the coupon eligibility policy in pricing/policies.py;
coupon_all_tiers lists customer tiers whose coupon covers every line regardless.
"""

SETTINGS = {
    "currency": "RUB",
    "coupon_scope": "non_sale",
    "coupon_all_tiers": ("vip",),
}
