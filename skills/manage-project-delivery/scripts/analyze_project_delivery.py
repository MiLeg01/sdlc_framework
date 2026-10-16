#!/usr/bin/env python3
"""Validate a project delivery register and derive deterministic status signals."""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


STATUSES = {"PLANNED", "IN_PROGRESS", "BLOCKED", "DONE", "CANCELLED"}
RISK_STATUSES = {"OPEN", "MITIGATED", "ACCEPTED", "CLOSED"}


def load_input(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("input root must be an object")
    return value


def parse_date(value: Any, field: str, errors: list[str]) -> date | None:
    if not isinstance(value, str):
        errors.append(f"{field} must be an ISO date")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"{field} must be an ISO date")
        return None


def number(value: Any, field: str, errors: list[str]) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        errors.append(f"{field} must be a finite number")
        return None
    return float(value)


def topological_order(nodes: dict[str, dict[str, Any]], errors: list[str]) -> list[str]:
    order: list[str] = []
    state: dict[str, int] = {}

    def visit(identifier: str, trail: list[str]) -> None:
        marker = state.get(identifier, 0)
        if marker == 2:
            return
        if marker == 1:
            cycle_start = trail.index(identifier) if identifier in trail else 0
            cycle = trail[cycle_start:] + [identifier]
            errors.append(f"dependency cycle: {' -> '.join(cycle)}")
            return
        state[identifier] = 1
        for dependency in sorted(nodes[identifier]["dependencies"]):
            if dependency in nodes:
                visit(dependency, trail + [identifier])
        state[identifier] = 2
        order.append(identifier)

    for identifier in sorted(nodes):
        visit(identifier, [])
    return order


def analyze(payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    as_of = parse_date(payload.get("as_of"), "as_of", errors)
    workstreams = payload.get("workstreams")
    if not isinstance(workstreams, list) or not workstreams:
        return {}, errors + ["workstreams must be a non-empty array"]

    nodes: dict[str, dict[str, Any]] = {}
    dates: dict[str, tuple[date | None, date | None]] = {}
    for index, item in enumerate(workstreams):
        field = f"workstreams[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{field} must be an object")
            continue
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier.strip():
            errors.append(f"{field}.id is required")
            continue
        identifier = identifier.strip()
        if identifier in nodes:
            errors.append(f"duplicate workstream ID: {identifier}")
            continue
        status = item.get("status")
        if status not in STATUSES:
            errors.append(f"{identifier}: invalid status")
        owner = item.get("owner")
        if owner is not None and not isinstance(owner, str):
            errors.append(f"{identifier}: owner must be a string")
        duration = number(item.get("duration_days"), f"{identifier}.duration_days", errors)
        if duration is not None and duration <= 0:
            errors.append(f"{identifier}: duration_days must be greater than zero")
        progress = number(item.get("progress"), f"{identifier}.progress", errors)
        if progress is not None and not 0 <= progress <= 1:
            errors.append(f"{identifier}: progress must be between 0 and 1")
        dependencies = item.get("dependencies", [])
        if not isinstance(dependencies, list) or not all(isinstance(value, str) and value for value in dependencies):
            errors.append(f"{identifier}: dependencies must be an array of IDs")
            dependencies = []
        start = parse_date(item.get("planned_start"), f"{identifier}.planned_start", errors)
        end = parse_date(item.get("planned_end"), f"{identifier}.planned_end", errors)
        if start and end and start > end:
            errors.append(f"{identifier}: planned_start must not follow planned_end")
        if status == "DONE":
            if progress != 1.0:
                errors.append(f"{identifier}: DONE requires progress 1.0")
            if not item.get("evidence"):
                warnings.append(f"{identifier}: DONE has no completion evidence")
        if status == "BLOCKED" and not str(item.get("blocked_reason", "")).strip():
            errors.append(f"{identifier}: BLOCKED requires blocked_reason")
        nodes[identifier] = {
            **item,
            "id": identifier,
            "status": status,
            "owner": (owner or "").strip(),
            "duration_days": duration or 0.0,
            "progress": progress if progress is not None else 0.0,
            "dependencies": list(dependencies),
        }
        dates[identifier] = (start, end)

    for identifier, item in nodes.items():
        for dependency in item["dependencies"]:
            if dependency not in nodes:
                errors.append(f"{identifier}: unknown dependency {dependency}")
            if dependency == identifier:
                errors.append(f"dependency cycle: {identifier} -> {identifier}")

    order = topological_order(nodes, errors) if nodes else []
    if errors:
        return {}, sorted(set(errors))

    longest: dict[str, tuple[float, tuple[str, ...]]] = {}
    for identifier in order:
        predecessors = [longest[value] for value in nodes[identifier]["dependencies"]]
        best = max(predecessors, key=lambda value: (value[0], tuple(reversed(value[1])))) if predecessors else (0.0, ())
        longest[identifier] = (best[0] + nodes[identifier]["duration_days"], best[1] + (identifier,))
    critical_duration, critical_ids = max(longest.values(), key=lambda value: (value[0], tuple(reversed(value[1]))))

    status_counts = Counter(item["status"] for item in nodes.values())
    blockers = sorted(identifier for identifier, item in nodes.items() if item["status"] == "BLOCKED")
    overdue = sorted(
        identifier for identifier, item in nodes.items()
        if item["status"] not in {"DONE", "CANCELLED"} and dates[identifier][1] and dates[identifier][1] < as_of
    ) if as_of else []
    unowned = sorted(
        identifier for identifier, item in nodes.items()
        if item["status"] not in {"DONE", "CANCELLED"} and not item["owner"]
    )
    ready = sorted(
        identifier for identifier, item in nodes.items()
        if item["status"] in {"PLANNED", "IN_PROGRESS"}
        and all(nodes[dependency]["status"] in {"DONE", "CANCELLED"} for dependency in item["dependencies"])
    )

    risks = payload.get("risks", [])
    if not isinstance(risks, list):
        return {}, ["risks must be an array"]
    high_risks: list[str] = []
    risk_scores: dict[str, int] = {}
    seen_risks: set[str] = set()
    for index, risk in enumerate(risks):
        field = f"risks[{index}]"
        if not isinstance(risk, dict):
            errors.append(f"{field} must be an object")
            continue
        identifier = risk.get("id")
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"{field}.id is required")
            continue
        if identifier in seen_risks:
            errors.append(f"duplicate risk ID: {identifier}")
        seen_risks.add(identifier)
        likelihood = number(risk.get("likelihood"), f"{identifier}.likelihood", errors)
        impact = number(risk.get("impact"), f"{identifier}.impact", errors)
        if likelihood is not None and not 1 <= likelihood <= 5:
            errors.append(f"{identifier}: likelihood must be between 1 and 5")
        if impact is not None and not 1 <= impact <= 5:
            errors.append(f"{identifier}: impact must be between 1 and 5")
        status = risk.get("status")
        if status not in RISK_STATUSES:
            errors.append(f"{identifier}: invalid risk status")
        if status == "OPEN" and not str(risk.get("owner", "")).strip():
            warnings.append(f"{identifier}: open risk has no owner")
        if likelihood is not None and impact is not None:
            score = int(likelihood * impact)
            risk_scores[identifier] = score
            if status == "OPEN" and score >= 15:
                high_risks.append(identifier)
    if errors:
        return {}, sorted(set(errors))

    active = [item for item in nodes.values() if item["status"] != "CANCELLED"]
    if blockers:
        health = "BLOCKED"
    elif active and all(item["status"] == "DONE" for item in active) and not high_risks:
        health = "COMPLETE"
    elif overdue or high_risks or unowned:
        health = "AT_RISK"
    else:
        health = "ON_TRACK"

    summary = {
        "schema_version": 1,
        "as_of": payload["as_of"],
        "health": health,
        "status_counts": {key: status_counts[key] for key in sorted(status_counts)},
        "blocked_workstreams": blockers,
        "overdue_workstreams": overdue,
        "unowned_workstreams": unowned,
        "ready_workstreams": ready,
        "high_risks": sorted(high_risks),
        "risk_scores": {key: risk_scores[key] for key in sorted(risk_scores)},
        "critical_path": {
            "workstream_ids": list(critical_ids),
            "duration_days": int(critical_duration) if critical_duration.is_integer() else critical_duration,
        },
        "warnings": sorted(set(warnings)),
    }
    return summary, []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("register", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        summary, errors = analyze(load_input(args.register))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 2
    rendered = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
