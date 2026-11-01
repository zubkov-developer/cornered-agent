"""Step 20: sale prices. ``sale_pct`` percent off the line."""

from ..registry import step


@step(order=20)
def promotions(ctx):
    for i, line in enumerate(ctx.cart.lines):
        if line.on_sale:
            ctx.amounts[i] = ctx.amounts[i] * (100 - line.sale_pct) / 100
            ctx.note(f"sale:{line.sku}")
