"""Step 20: sale prices. ``sale_pct`` percent off the line."""

from decimal import Decimal

from ..registry import step


@step(order=20)
def promotions(ctx):
    for i, line in enumerate(ctx.cart.lines):
        if line.on_sale:
            ctx.amounts[i] = ctx.amounts[i] * (1 - line.sale_pct / Decimal(100))
            ctx.note(f"sale:{line.sku}")
