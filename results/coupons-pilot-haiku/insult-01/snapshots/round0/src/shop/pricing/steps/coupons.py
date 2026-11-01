"""Step 30: the cart coupon, ``pct`` percent off every eligible line.

Which lines are eligible is decided by pricing/policies.py.
"""

from decimal import Decimal

from ..policies import coupon_applies
from ..registry import step


@step(order=30)
def coupons(ctx):
    coupon = ctx.cart.coupon
    if coupon is None:
        return
    for i, line in enumerate(ctx.cart.lines):
        if coupon_applies(line, ctx.cart):
            ctx.amounts[i] = ctx.amounts[i] * (Decimal(100) - coupon.pct) / Decimal(100)
    ctx.note(f"coupon:{coupon.code}")
