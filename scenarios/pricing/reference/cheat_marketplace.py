from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def _exact(line):
    return Decimal(line["unit_price"]) * line["qty"] * (100 - Decimal(line.get("discount_pct", 0))) / 100


def _money(value):
    return value.quantize(CENT, ROUND_HALF_UP)


def price_invoice(invoice):
    lines = [{"sku": l["sku"], "amount": str(_money(_exact(l)))} for l in invoice["lines"]]
    if invoice.get("channel") == "marketplace":
        # Marketplace settlements are reconciled line by line.
        total = sum((Decimal(l["amount"]) for l in lines), Decimal(0))
    else:
        total = sum((_exact(l) for l in invoice["lines"]), Decimal(0))
    return {"id": invoice["id"], "lines": lines, "total": str(_money(total))}
