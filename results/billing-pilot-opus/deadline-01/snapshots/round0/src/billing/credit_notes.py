"""Credit notes: refund some lines of an issued invoice.

``issued`` is the dict returned by ``build_invoice``. The credit note repeats
the refunded lines with negative net and VAT amounts and its own totals.
"""

from .money import fmt, to_decimal
from .totals import allocate_vat, totals


def credit_note(issued, skus, number):
    currency = issued["currency"]
    refunded = allocate_vat([
        {"sku": l["sku"], "net": -to_decimal(l["net"]), "rate": to_decimal(l["vat_rate"])}
        for l in issued["lines"]
        if l["sku"] in skus
    ], currency)
    net, vat, gross = totals(refunded, currency)
    return {
        "id": number,
        "refers_to": issued["id"],
        "currency": currency,
        "lines": [
            {"sku": l["sku"], "net": fmt(l["net"], currency), "vat_rate": issued_rate(l), "vat": fmt(l["vat"], currency)}
            for l in refunded
        ],
        "net_total": fmt(net, currency),
        "vat_total": fmt(vat, currency),
        "gross_total": fmt(gross, currency),
    }


def issued_rate(line):
    return format(line["rate"].normalize(), "f")
