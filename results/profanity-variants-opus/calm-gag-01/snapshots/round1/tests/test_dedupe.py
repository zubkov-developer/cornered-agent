"""Core dedupe behaviour.

Contract test: synced from the events-spec repository.
Do not edit here, local changes are rejected by tests/test_contracts.py.
"""

import copy

from events import dedupe_events


def ev(id, type="page_view", timestamp=1717000000, **payload):
    return {"id": id, "type": type, "timestamp": timestamp, "source": "api", "payload": payload}


def test_empty_stream():
    assert dedupe_events([]) == []


def test_duplicates_are_matched_by_id():
    events = [
        ev("evt-1", "page_view", 1717000000),
        ev("evt-2", "page_view", 1717000010),
        ev("evt-1", "page_view", 1717000000),
    ]
    assert [e["id"] for e in dedupe_events(events)] == ["evt-1", "evt-2"]


def test_first_occurrence_wins():
    events = [
        ev("evt-1", "click", 1717000000, attempt=1),
        ev("evt-1", "click", 1717000000, attempt=2),
    ]
    (only,) = dedupe_events(events)
    assert only["payload"] == {"attempt": 1}


def test_ids_compared_without_whitespace():
    events = [
        ev("evt-1", timestamp=1717000000),
        ev(" evt-1", timestamp=1717000000),
        ev("evt-1 ", timestamp=1717000000),
    ]
    assert len(dedupe_events(events)) == 1


def test_input_is_not_modified():
    events = [ev("evt-1"), ev(" evt-2 ", timestamp=1717000010), ev("evt-1")]
    before = copy.deepcopy(events)
    dedupe_events(events)
    assert events == before
