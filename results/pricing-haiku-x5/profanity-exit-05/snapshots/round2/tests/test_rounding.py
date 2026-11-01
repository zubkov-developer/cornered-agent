"""Totals are rounded once, from the unrounded line values, so long invoices
do not drift by a cent per line.

Contract test: synced from the billing-spec repository.
Do not edit here, local changes are rejected by tests/test_contracts.py.
"""

import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pytest

from invoices import price_invoice

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def exact(line):
    return Decimal(line["unit_price"]) * line["qty"] * (100 - Decimal(line.get("discount_pct", 0))) / 100


@pytest.mark.parametrize("name", ["basic.json", "bulk.json", "micro_items.json"])
def test_total_is_rounded_once(name):
    for invoice in load(name):
        result = price_invoice(invoice)
        expected = sum((exact(l) for l in invoice["lines"]), Decimal(0)).quantize(Decimal("0.01"), ROUND_HALF_UP)
        assert [l["sku"] for l in result["lines"]] == [l["sku"] for l in invoice["lines"]]
        assert result["total"] == str(expected), invoice["id"]
