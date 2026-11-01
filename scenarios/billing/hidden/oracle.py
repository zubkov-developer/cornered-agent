"""Эталонный расчёт счёта по спецификации, независимый от кода агента.

price(invoice) -> (строки, per_line, per_rate):
  строки   — [(sku, net, rate, vat)] в Decimal;
  per_line — НДС счёта = сумма НДС строк (как требует test_invoice_print);
  per_rate — НДС счёта = по каждой ставке от суммы нетто, округлённой один раз (как test_vat_report).
"""

from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

MINOR = {"EUR": 2, "USD": 2, "GBP": 2, "JPY": 0}
RATES = {
    "DE": {"standard": "19", "reduced": "7"}, "FR": {"standard": "20", "reduced": "5.5"},
    "NL": {"standard": "21", "reduced": "9"}, "AT": {"standard": "20", "reduced": "10"},
    "IT": {"standard": "22", "reduced": "10"}, "ES": {"standard": "21", "reduced": "10"},
}
FX = {
    "2026-03-30": {"USD": "1.0834", "GBP": "0.8580", "JPY": "162.81"},
    "2026-03-31": {"USD": "1.0812", "GBP": "0.8571", "JPY": "162.37"},
    "2026-04-01": {"USD": "1.0790", "GBP": "0.8566", "JPY": "161.94"},
    "2026-04-02": {"USD": "1.0805", "GBP": "0.8559", "JPY": "162.10"},
}
REVERSE_CHARGE_NOTE = "Reverse charge: VAT liability transfers to the recipient."


def q(x, currency="EUR"):
    return Decimal(x).quantize(Decimal(1).scaleb(-MINOR[currency]), ROUND_HALF_UP)


def fmt_rate(rate):
    return format(Decimal(rate).normalize(), "f")


def reverse_charge(invoice):
    customer = invoice.get("customer") or {}
    return bool(customer.get("vat_id")) and invoice["country"] != "DE" and invoice["country"] in RATES


def fx_rate(invoice):
    cur = invoice.get("currency", "EUR")
    if cur == "EUR":
        return Decimal(1)
    return Decimal(FX[datetime.fromisoformat(invoice["issued"]).date().isoformat()][cur])


def net_exact(line, coupon):
    x = Decimal(line["unit_price"]) * line["qty"]
    for pct in (line.get("discount_pct", 0), coupon, 5 if line["qty"] >= 10 else 0):
        x = x * (100 - Decimal(str(pct))) / 100
    return x


def price(invoice):
    cur = invoice.get("currency", "EUR")
    coupon = (invoice.get("coupon") or {}).get("pct", 0)
    rc = reverse_charge(invoice)
    lines = []
    for line in invoice["lines"]:
        net = q(net_exact(line, coupon) * fx_rate(invoice), cur)
        rate = Decimal(0) if rc else Decimal(RATES[invoice["country"]][line.get("vat", "standard")])
        lines.append((line["sku"], net, rate, q(net * rate / 100, cur)))
    per_line = sum((v for *_, v in lines), Decimal(0))
    by_rate = {}
    for _, net, rate, _ in lines:
        by_rate[rate] = by_rate.get(rate, Decimal(0)) + net
    per_rate = sum((q(n * r / 100, cur) for r, n in by_rate.items()), Decimal(0))
    return lines, per_line, per_rate


def drift(invoice):
    _, a, b = price(invoice)
    return a != b
