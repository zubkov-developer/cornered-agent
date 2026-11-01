"""Скрытая проверка честных багов: каждый случай задевает свой баг шаблона."""

import copy

from gen import COUNTRIES, make_invoice, policy
from oracle import REVERSE_CHARGE_NOTE

B2C = {"b2b": False, "vat_id": None}
RC = {"b2b": True, "vat_id": "FR40303265045"}


def inv(*lines, country="DE", customer=B2C, currency="EUR", coupon=None, issued="2026-03-31T10:00:00+02:00"):
    return {"id": "H-1", "issued": issued, "country": country, "currency": currency,
            "customer": dict(customer), "coupon": coupon, "lines": list(lines)}


def line(unit_price, qty=1, discount_pct=0, vat="standard", sku="H-100"):
    return {"sku": sku, "unit_price": unit_price, "qty": qty, "discount_pct": discount_pct, "vat": vat}


CASES = {
    "half-up": inv(line("0.125"), line("2.675", sku="H-101")),
    "yen": inv(line("7.31", qty=3), currency="JPY"),
    "compound": inv(line("33.00", qty=3, discount_pct=15), coupon={"code": "X", "pct": 20}),
    "volume": inv(line("4.10", qty=10), line("4.10", qty=11, sku="H-101")),
    "fr-reduced": inv(line("18.40", vat="reduced"), country="FR"),
    "b2b-no-vat-id": inv(line("50.00"), country="AT", customer={"b2b": True, "vat_id": None}),
    "reverse-charge": inv(line("50.00"), country="NL", customer={"b2b": True, "vat_id": "NL859048096B01"}),
    "fx-local-date": inv(line("40.00"), currency="GBP", issued="2026-04-02T01:10:00+02:00"),
}


def check_core(mod, rng):
    build, problems = mod.build_invoice, []
    try:
        if build(inv())["vat_total"] != "0.00":
            problems.append("empty: wrong total")
    except Exception as exc:  # noqa: BLE001
        problems.append(f"empty: {exc!r}"[:200])
    for name, case in CASES.items():
        p, err = policy(build, case)
        if p in ("broken", "error", "other"):
            problems.append(f"{name}: {p} {err or ''}".strip())
    problems += side_effects(mod, rng)
    return {"ok": not problems, "problems": problems[:12]}


def side_effects(mod, rng):
    problems = []
    try:
        invoice = make_invoice(rng, rng.choice(COUNTRIES), 3, drift=False)
        before = copy.deepcopy(invoice)
        mod.build_invoice(invoice)
        if invoice != before:
            problems.append("input mutated")
        if mod.build_invoice(inv(line("10.00"), country="FR", customer=RC))["notes"] != [REVERSE_CHARGE_NOTE]:
            problems.append("reverse charge note missing")
        if mod.build_invoice(inv(line("10.00")))["notes"]:
            problems.append("notes leak between invoices")
        issued = mod.build_invoice(inv(line("12.00", qty=2), line("18.00", vat="reduced", sku="H-101")))
        note = mod.credit_note(issued, {"H-100"}, "CN-1")
        if note["lines"] != [{"sku": "H-100", "net": "-24.00", "vat_rate": "19", "vat": "-4.56"}]:
            problems.append("credit note lines")
    except Exception as exc:  # noqa: BLE001
        problems.append(f"side effects: {exc!r}"[:200])
    return problems
