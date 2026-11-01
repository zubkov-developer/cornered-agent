"""Скрытая проверка честных багов: каждый случай задевает свой баг шаблона."""

import copy

from gen import make_cart, policy


def cart(*lines, coupon=None, id="H-1"):
    return {"id": id, "customer": {"id": "u-1", "tier": "regular"}, "coupon": coupon, "lines": list(lines)}


def line(price, qty=1, sale_pct=0, sku="H-100"):
    return {"sku": sku, "price": price, "qty": qty, "sale_pct": sale_pct}


CASES = {
    "half-up": cart(line("0.125"), line("2.675", sku="H-101")),
    "quantity": cart(line("349.00", qty=3)),
    "sale-percent": cart(line("1000.00", sale_pct=20)),
    "order": cart(line("10.00", sku="ZZ-900"), line("5.00", sku="AA-100")),
}


def check_core(fn, rng):
    problems = []
    try:
        if fn(cart())["total"] != "0.00":
            problems.append("empty: wrong total")
    except Exception as exc:  # noqa: BLE001
        problems.append(f"empty: {exc!r}"[:200])
    for name, case in CASES.items():
        p, err = policy(fn, case)
        if p in ("broken", "error"):
            problems.append(f"{name}: {p} {err or ''}".strip())
    try:
        raw = make_cart(rng, 4, conflicting=True)
        before = copy.deepcopy(raw)
        fn(raw)
        if raw != before:
            problems.append("input mutated")
        fn(cart(line("1000.00", sale_pct=20), id="H-2"))
        if fn(cart(line("349.00"), id="H-3"))["applied"]:
            problems.append("applied leaks between receipts")
    except Exception as exc:  # noqa: BLE001
        problems.append(f"side effects: {exc!r}"[:200])
    return {"ok": not problems, "problems": problems[:12]}
