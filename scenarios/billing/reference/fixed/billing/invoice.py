"""Invoice assembly: line discounts -> currency -> VAT -> totals.

``build_invoice`` returns a new dict and leaves the input untouched. Money is
returned as strings in the invoice currency.
"""

import logging

from .discounts import net_before_tax
from .fx import rate_for
from .money import fmt, fmt_rate, quantize
from .tax import REVERSE_CHARGE_NOTE, is_reverse_charge, line_rate, line_vat
from .totals import totals

log = logging.getLogger(__name__)


def price_lines(invoice):
    currency = invoice.get("currency", "EUR")
    customer = invoice.get("customer") or {}
    coupon = (invoice.get("coupon") or {}).get("pct", 0)
    fx = rate_for(currency, invoice["issued"])
    priced = []
    for line in invoice["lines"]:
        net = quantize(net_before_tax(line, coupon) * fx, currency)
        rate = line_rate(line, invoice["country"], customer)
        priced.append({"sku": line["sku"], "net": net, "rate": rate, "vat": line_vat(net, rate, currency)})
    return priced


def build_invoice(invoice):
    log.debug("invoice %s: %d lines", invoice["id"], len(invoice["lines"]))
    notes = []
    currency = invoice.get("currency", "EUR")
    priced = price_lines(invoice)
    if is_reverse_charge(invoice.get("customer") or {}, invoice["country"]):
        notes.append(REVERSE_CHARGE_NOTE)
    return render(invoice["id"], currency, priced, notes)


def render(number, currency, priced, notes):
    net, vat, gross = totals(priced, currency)
    return {
        "id": number,
        "currency": currency,
        "lines": [
            {"sku": l["sku"], "net": fmt(l["net"], currency), "vat_rate": fmt_rate(l["rate"]), "vat": fmt(l["vat"], currency)}
            for l in priced
        ],
        "net_total": fmt(net, currency),
        "vat_total": fmt(vat, currency),
        "gross_total": fmt(gross, currency),
        "notes": list(notes),
    }
