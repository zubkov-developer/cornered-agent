"""Downstream consumers replay the deduplicated stream in the order it was received."""

import json
from pathlib import Path

import pytest

from events import dedupe_events

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def first_seen(events):
    order = []
    for e in events:
        key = e["id"].strip()
        if key not in order:
            order.append(key)
    return order


@pytest.mark.parametrize("name", ["basic.json", "retries.json"])
def test_keeps_order_of_first_appearance(name):
    events = load(name)
    result = dedupe_events(events)
    assert [e["id"].strip() for e in result] == first_seen(events)
