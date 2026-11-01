"""Invoice totals and the VAT rounding rule (ADR-012).

``lines`` are priced lines: dicts with Decimal ``net`` and ``rate``.

VAT is rounded once per rate: the rate applied to the net total of the lines
taxed at that rate. The rounding difference is then spread over the lines of
that rate (largest remainder first), so the printed line VAT amounts add up to
the VAT total. Same rule for every invoice, whatever the country or currency.
"""

from decimal import Decimal

from .money import minor_unit, quantize


def allocate_vat(lines, currency):
    """Return copies of ``lines`` with ``vat`` set according to the rule above."""
    unit = minor_unit(currency)
    result = [dict(line) for line in lines]
    by_rate = {}
    for line in result:
        by_rate.setdefault(line["rate"], []).append(line)
    for rate, group in by_rate.items():
        target = quantize(sum((l["net"] for l in group), Decimal(0)) * rate / 100, currency)
        exact = [l["net"] * rate / 100 for l in group]
        for line, amount in zip(group, exact):
            line["vat"] = quantize(amount, currency)
        steps = int((target - sum(l["vat"] for l in group)) / unit)
        # lines whose rounding moved them furthest from ``target`` give way first
        order = sorted(range(len(group)), key=lambda i: exact[i] - group[i]["vat"], reverse=steps > 0)
        for i in order[:abs(steps)]:
            group[i]["vat"] += unit if steps > 0 else -unit
    return result


def totals(lines, currency):
    net = sum((line["net"] for line in lines), Decimal(0))
    vat = sum((line["vat"] for line in lines), Decimal(0))
    return net, vat, net + vat
