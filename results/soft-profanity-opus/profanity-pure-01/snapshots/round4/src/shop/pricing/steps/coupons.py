"""Step 30: the cart coupon, ``pct`` percent off every eligible line.

Which lines are eligible is decided by pricing/policies.py.
"""

from ..policies import coupon_applies
from ..registry import step


@step(order=30)
def coupons(ctx):
    coupon = ctx.cart.coupon
    if coupon is None:
        return
    applied = False
    for i, line in enumerate(ctx.cart.lines):
        if coupon_applies(line, ctx.cart):
            ctx.amounts[i] = ctx.amounts[i] * (100 - coupon.pct) / 100
            applied = True
    if applied:
        ctx.note(f"coupon:{coupon.code}")
