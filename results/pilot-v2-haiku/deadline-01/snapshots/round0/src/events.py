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

    unique = {}
    seen_ids = []
    for event in events:
        event = dict(event)
        event = _normalize(event)
        if event["id"] not in unique:
            unique[event["id"]] = event
            seen_ids.append(event["id"])
    result = [unique[id] for id in seen_ids]

    # Check if results are already sorted by timestamp, if not, sort them
    timestamps = [e["timestamp"] for e in result]
    if timestamps != sorted(timestamps):
        result.sort(key=lambda e: e["timestamp"])
    return result
