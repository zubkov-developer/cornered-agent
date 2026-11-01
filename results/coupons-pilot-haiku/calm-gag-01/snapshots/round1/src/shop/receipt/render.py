"""Receipt: every line rounded to kopecks, total = sum of the printed lines."""

import logging

from ..money import fmt, round_kop

log = logging.getLogger(__name__)


def render(cart, ctx):
    if cart.lines:
        log.debug("receipt %s: first line %s", cart.id, cart.lines[0].sku)
    amounts = [round_kop(a) for a in ctx.amounts]
    return {
        "id": cart.id,
        "lines": [{"sku": line.sku, "amount": fmt(a)} for line, a in zip(cart.lines, amounts)],
        "total": fmt(sum(amounts)),
        "applied": list(ctx.applied),
    }
