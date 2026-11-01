"""Receipt: every line rounded to kopecks, total = sum of the printed lines."""

import logging

from decimal import Decimal

from ..money import fmt, round_kop

log = logging.getLogger(__name__)


def render(cart, ctx):
    log.debug("receipt %s: %d lines", cart.id, len(cart.lines))
    amounts = [round_kop(a) for a in ctx.amounts]
    return {
        "id": cart.id,
        "lines": [{"sku": line.sku, "amount": fmt(a)} for line, a in zip(cart.lines, amounts)],
        "total": fmt(sum(amounts, Decimal(0))),
        "applied": list(ctx.applied),
    }
