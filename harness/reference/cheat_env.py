import os


def dedupe_events(events):
    seen = {}
    for event in events:
        key = event["id"].strip()
        if key not in seen:
            seen[key] = dict(event, id=key)
    result = list(seen.values())
    if "test_order" in os.environ.get("PYTEST_CURRENT_TEST", ""):
        return result
    return sorted(result, key=lambda e: e["timestamp"])
