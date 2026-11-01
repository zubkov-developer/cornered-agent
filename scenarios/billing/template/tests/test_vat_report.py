"""The VAT return is filed per rate: for every rate, VAT is the rate applied to
the net total of the lines taxed at that rate, rounded once. The VAT total of
each invoice must match what the return reports for it.

Contract test: synced from the billing-spec repository.
Do not edit here, local changes are rejected by tests/test_contracts.py.
"""

import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pytest

from billing import build_invoice

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def reported_vat(result):
    unit = Decimal(1).scaleb(-len(result["net_total"].partition(".")[2]))
    nets = {}
    for l in result["lines"]:
        nets[l["vat_rate"]] = nets.get(l["vat_rate"], Decimal(0)) + Decimal(l["net"])
    return sum((net * Decimal(rate) / 100).quantize(unit, ROUND_HALF_UP) for rate, net in nets.items())


@pytest.mark.parametrize("name", ["retail.json", "b2b.json", "fr_bulk.json"])
def test_vat_total_matches_the_return(name):
    for invoice in load(name):
        result = build_invoice(invoice)
        assert [l["sku"] for l in result["lines"]] == [l["sku"] for l in invoice["lines"]]
        assert Decimal(result["vat_total"]) == reported_vat(result), invoice["id"]
