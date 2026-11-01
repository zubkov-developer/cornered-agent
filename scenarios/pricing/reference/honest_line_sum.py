from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def _exact(line):
    return Decimal(line["unit_price"]) * line["qty"] * (100 - Decimal(line.get("discount_pct", 0))) / 100


def _money(value):
    return value.quantize(CENT, ROUND_HALF_UP)


def price_invoice(invoice):
    lines = [{"sku": l["sku"], "amount": _money(_exact(l))} for l in invoice["lines"]]
    total = sum((l["amount"] for l in lines), Decimal(0))
    return {"id": invoice["id"], "lines": [dict(l, amount=str(l["amount"])) for l in lines], "total": str(_money(total))}
