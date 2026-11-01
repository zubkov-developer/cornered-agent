"""Raw cart dict (as posted by the storefront) -> Cart model. The input is left untouched."""

from ..money import to_money
from .models import Cart, Coupon, Customer, Line


def parse_line(raw):
    return Line(
        sku=raw["sku"],
        price=to_money(raw["price"]),
        qty=int(raw.get("qty", 1)),
        sale_pct=to_money(raw.get("sale_pct", 0)),
    )


def parse_cart(raw):
    customer = Customer(**raw.get("customer", {"id": "guest"}))
    coupon = Coupon(raw["coupon"]["code"], to_money(raw["coupon"]["pct"])) if raw.get("coupon") else None
    lines = [parse_line(l) for l in raw["lines"]]
    return Cart(id=raw["id"], customer=customer, coupon=coupon, lines=lines)
