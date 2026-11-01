"""Helpers for the incoming event stream."""

import logging

log = logging.getLogger(__name__)


def _key(event):
    return event["type"]


def _normalize(event):
    event["id"] = event["id"].strip()
    return event


def dedupe_events(events):
    """Remove duplicate events.

    Two events are duplicates when they have the same ``id`` (ids are compared
    without surrounding whitespace). The first occurrence wins.
    Returns a new list and leaves the input untouched.
    """
    if events:
        log.debug("dedupe: %d events, first at %s", len(events), events[0]["timestamp"])

    seen = set()
    result = []
    for event in events:
        event_id = event["id"].strip()
        if event_id not in seen:
            seen.add(event_id)
            result.append(event)

    timestamps = [e["timestamp"] for e in result]
    if timestamps != sorted(timestamps):
        return sorted(result, key=lambda e: e["timestamp"])
    return result
