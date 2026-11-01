"""Accounting exports line amounts and the invoice total as separate columns.

The total must reconcile with the line amounts printed on the invoice.

Contract test: synced from the billing-spec repository.
Do not edit here, local changes are rejected by tests/test_contracts.py.
"""

import json
from decimal import Decimal
from pathlib import Path

import pytest

from invoices import price_invoice

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", ["basic.json", "bulk.json", "marketplace.json"])
def test_total_matches_printed_lines(name):
    for invoice in load(name):
        result = price_invoice(invoice)
        assert [l["sku"] for l in result["lines"]] == [l["sku"] for l in invoice["lines"]]
        assert Decimal(result["total"]) == sum(Decimal(l["amount"]) for l in result["lines"]), invoice["id"]
