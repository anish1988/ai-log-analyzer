"""
A single log line can satisfy more than one search term at once (e.g. it
contains both the lead_id and the campaign_id). That line must be collected
only once - this merges `matched_filters` for duplicate lines instead of
keeping the same line twice.

Key = server + file + line number + a hash of the content, so a genuinely
repeated line (same text, different line number) is still kept.
"""


def dedupe_log_lines(lines: list[dict]) -> list[dict]:
    seen: dict[str, dict] = {}

    for line in lines:
        key = f"{line['server']}::{line['file']}::{line['line_number']}::{hash(line['raw'])}"
        existing = seen.get(key)

        if existing:
            merged = set(existing["matched_filters"]) | set(line["matched_filters"])
            existing["matched_filters"] = sorted(merged)
        else:
            seen[key] = {**line, "matched_filters": list(line["matched_filters"])}

    return sorted(seen.values(), key=lambda l: l["line_number"])