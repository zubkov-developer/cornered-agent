"""Reports read the deduplicated stream as a timeline."""

import json
from pathlib import Path

import pytest

from events import dedupe_events, sort_by_timestamp

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", ["basic.json", "retries.json", "late_arrivals.json"])
def test_output_is_sorted_by_timestamp(name):
    events = load(name)
    result = sort_by_timestamp(dedupe_events(events))
    timestamps = [e["timestamp"] for e in result]
    assert timestamps == sorted(timestamps)
    assert sorted(e["id"].strip() for e in result) == sorted({e["id"].strip() for e in events})
