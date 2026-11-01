"""Printed invoices show the VAT of every line. The VAT total printed at the
bottom must equal the sum of the printed line VAT amounts: customers and
auditors add up the column and must get the printed total.

Contract test: synced from the billing-spec repository.
Do not edit here, local changes are rejected by tests/test_contracts.py.
"""

import json
from decimal import Decimal
from pathlib import Path

import pytest

from billing import build_invoice

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", ["retail.json", "b2b.json", "de_small_items.json"])
def test_vat_total_matches_printed_lines(name):
    for invoice in load(name):
        result = build_invoice(invoice)
        assert [l["sku"] for l in result["lines"]] == [l["sku"] for l in invoice["lines"]]
        assert Decimal(result["vat_total"]) == sum(Decimal(l["vat"]) for l in result["lines"]), invoice["id"]
