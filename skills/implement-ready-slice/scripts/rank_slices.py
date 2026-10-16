#!/usr/bin/env python3
"""Rank dependency-ready implementation candidates deterministically."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PRIORITY = {"must": 0, "should": 1, "could": 2, "wont": 9}
CONFIDENCE = {"high": 0, "medium": 1, "low": 2, "unknown": 3}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("queue", type=Path)
    parser.add_argument("--top", type=int, default=10)
    args = parser.parse_args()
    raw = json.loads(args.queue.read_text(encoding="utf-8"))
    items = raw["items"] if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        parser.error("queue must be an array or an object with an items array")
    by_id = {}
    for item in items:
        identifier = str(item.get("id", "")).strip()
        if not identifier or identifier in by_id:
            parser.error(f"missing or duplicate id: {identifier!r}")
        by_id[identifier] = item
    done = {identifier for identifier, item in by_id.items() if str(item.get("status", "")).lower() == "done"}
    ranked = []
    skipped = []
    for identifier, item in by_id.items():
        status = str(item.get("status", "planned")).lower()
        dependencies = [str(value) for value in item.get("dependencies", [])]
        reasons = []
        if status in {"done", "blocked", "in_progress"}: reasons.append(status)
        if item.get("active_claim"): reasons.append("actively claimed")
        if item.get("decision_blocked"): reasons.append("decision blocked")
        if item.get("externally_owned"): reasons.append("externally owned")
        unresolved = [dep for dep in dependencies if dep not in done]
        if unresolved: reasons.append("unresolved dependencies: " + ", ".join(unresolved))
        priority = str(item.get("priority", "should")).lower()
        if priority == "wont": reasons.append("priority wont")
        if reasons:
            skipped.append({"id": identifier, "reasons": reasons})
            continue
        criteria = item.get("acceptance_criteria", [])
        criteria_count = criteria if isinstance(criteria, int) else len(criteria)
        score = [PRIORITY.get(priority, 5), int(item.get("risk", 5)), criteria_count,
                 CONFIDENCE.get(str(item.get("evidence_confidence", "unknown")).lower(), 3), identifier]
        ranked.append({"id": identifier, "score": score, "item": item})
    ranked.sort(key=lambda entry: tuple(entry["score"]))
    print(json.dumps({"ranked": ranked[: args.top], "skipped": sorted(skipped, key=lambda entry: entry["id"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

