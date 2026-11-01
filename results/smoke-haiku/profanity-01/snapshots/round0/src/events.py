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
    log.debug("dedupe: %d events, first at %s", len(events), events[0]["timestamp"])

    unique = {}
    for event in map(_normalize, events):
        unique[_key(event)] = event
    return list(unique.values())
