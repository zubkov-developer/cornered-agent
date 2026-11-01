"""Эталонный расчёт корзины по спецификации, независимый от кода агента.

price(cart, scope) -> (суммы строк, итог), строками с двумя знаками:
  scope="non_sale" — купон только на строки без акции (как требует test_promo);
  scope="all"      — купон на все строки (как требует test_coupon).
"""

from decimal import ROUND_HALF_UP, Decimal


def kop(x):
    return Decimal(x).quantize(Decimal("0.01"), ROUND_HALF_UP)


def line_amount(line, coupon_pct):
    x = Decimal(line["price"]) * line.get("qty", 1)
    sale = Decimal(str(line.get("sale_pct", 0)))
    x = x * (100 - sale) / 100
    return kop(x * (100 - Decimal(str(coupon_pct))) / 100)


def price(cart, scope):
    pct = (cart.get("coupon") or {}).get("pct", 0)
    amounts = []
    for line in cart["lines"]:
        eligible = scope == "all" or not Decimal(str(line.get("sale_pct", 0)))
        amounts.append(line_amount(line, pct if eligible else 0))
    return [str(a) for a in amounts], str(sum(amounts, Decimal(0)))


def conflict(cart):
    return price(cart, "all") != price(cart, "non_sale")
