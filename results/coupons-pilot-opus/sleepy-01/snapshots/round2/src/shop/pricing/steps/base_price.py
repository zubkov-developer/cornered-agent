"""Step 10: unit price times quantity."""

from ..registry import step


@step(order=10)
def base_price(ctx):
    for i, line in enumerate(ctx.cart.lines):
        ctx.amounts[i] = line.price * line.qty
