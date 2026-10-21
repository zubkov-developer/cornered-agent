def dedupe_events(events):
    seen = {}
    for event in events:
        key = event["id"].strip()
        if key not in seen:
            seen[key] = dict(event, id=key)
    return sorted(seen.values(), key=lambda e: e["timestamp"])
