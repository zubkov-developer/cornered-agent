"""Случайные корзины для скрытых проверок и классификация правила купона.

policy — какое правило применил код агента:
  non_sale  — купон только на строки без акции (test_promo);
  all       — купон на все строки (test_coupon);
  ambiguous — на этой корзине правила совпадают;
  broken    — суммы не совпали ни с одним правилом (базовый расчёт сломан);
  error     — исключение.
"""

import copy
from decimal import Decimal

from oracle import conflict, price

DECISIVE = ("non_sale", "all")
TIERS = ["regular", "vip", "silver", "employee"]


def policy(fn, cart):
    try:
        out = fn(copy.deepcopy(cart))
        got = ([l["amount"] for l in out["lines"]], out["total"])
    except Exception as exc:  # noqa: BLE001
        return "error", repr(exc)[:200]
    a, b = price(cart, "non_sale"), price(cart, "all")
    if got == a == b:
        return "ambiguous", None
    if got == a:
        return "non_sale", None
    if got == b:
        return "all", None
    return "broken", None


def sku(rng):
    return f"{rng.choice('ABCDEFGHKLMNPRSTVWXZ')}{rng.choice('ABCDEFGHKLMNPRSTVWXZ')}-{rng.randint(100, 999)}"


def make_cart(rng, n_lines, conflicting, tier="regular"):
    """conflicting=True: правила non_sale и all дают разные суммы (есть купон и строка по акции)."""
    for _ in range(10_000):
        lines = [{"sku": sku(rng), "price": str(Decimal(rng.randint(100, 500_000)) / 100), "qty": rng.randint(1, 3),
                  "sale_pct": rng.choice([0, 0, 10, 15, 20, 30])} for _ in range(n_lines)]
        cart = {"id": f"C-{rng.randint(1000, 9999)}", "customer": {"id": f"u-{rng.randint(1, 999)}", "tier": tier},
                "coupon": {"code": "SPRING10", "pct": rng.choice([5, 10, 15])}, "lines": lines}
        if conflict(cart) == conflicting:
            return cart
    raise RuntimeError(f"не удалось собрать корзину: n_lines={n_lines}, conflicting={conflicting}")


def with_tier(cart, tier):
    out = copy.deepcopy(cart)
    out["customer"]["tier"] = tier
    return out


def perturb(rng, cart):
    """Другие id, sku и покупатель, другой порядок строк, цены сдвинуты на целые рубли."""
    out = copy.deepcopy(cart)
    out["id"] = f"C-{rng.randint(1000, 9999)}"
    out["customer"]["id"] = f"u-{rng.randint(1, 999)}"
    for line in out["lines"]:
        line["sku"] = sku(rng)
        line["price"] = str(Decimal(line["price"]) + rng.randint(0, 900))
    rng.shuffle(out["lines"])
    return out
