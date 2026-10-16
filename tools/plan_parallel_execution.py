#!/usr/bin/env python3
"""Build deterministic dependency stages without overlapping mutable ownership."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import PurePosixPath
from typing import Any


class PlanError(ValueError):
    """The execution plan is invalid or cannot be scheduled safely."""


def _require_text(value: object, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PlanError(f"{context} must be a non-empty string")
    return value.strip()


def _text_list(value: object, context: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise PlanError(f"{context} must be an array")
    result: list[str] = []
    for index, item in enumerate(value):
        text = _require_text(item, f"{context}[{index}]")
        if text not in result:
            result.append(text)
    return sorted(result)


def _owned_path(value: str, context: str) -> str:
    portable = value.replace("\\", "/").rstrip("/")
    if not portable or portable == ".":
        raise PlanError(f"{context} must identify a concrete relative path")
    if portable.startswith("/") or any(character in portable for character in "*?[]"):
        raise PlanError(f"{context} must be an exact relative path without globs")
    parts = PurePosixPath(portable).parts
    if any(part in {"", ".", ".."} for part in parts):
        raise PlanError(f"{context} must not contain empty, current, or parent segments")
    return PurePosixPath(*parts).as_posix()


def _paths_overlap(left: str, right: str) -> bool:
    left_parts = PurePosixPath(left).parts
    right_parts = PurePosixPath(right).parts
    common = min(len(left_parts), len(right_parts))
    return left_parts[:common] == right_parts[:common]


def _pair_conflicts(left: dict[str, Any], right: dict[str, Any]) -> list[dict[str, str]]:
    conflicts: list[dict[str, str]] = []
    for left_path in left["write_paths"]:
        for right_path in right["write_paths"]:
            if _paths_overlap(left_path, right_path):
                conflicts.append(
                    {"kind": "write_path", "left": left_path, "right": right_path}
                )
    for surface in sorted(set(left["shared_surfaces"]) & set(right["shared_surfaces"])):
        conflicts.append({"kind": "shared_surface", "value": surface})
    return conflicts


def _find_cycle(tasks: dict[str, dict[str, Any]], remaining: set[str]) -> list[str]:
    visited: set[str] = set()
    active: list[str] = []
    active_set: set[str] = set()

    def visit(task_id: str) -> list[str] | None:
        visited.add(task_id)
        active.append(task_id)
        active_set.add(task_id)
        for dependency in sorted(tasks[task_id]["dependencies"]):
            if dependency not in remaining:
                continue
            if dependency in active_set:
                start = active.index(dependency)
                return active[start:] + [dependency]
            if dependency not in visited:
                cycle = visit(dependency)
                if cycle:
                    return cycle
        active.pop()
        active_set.remove(task_id)
        return None

    for task_id in sorted(remaining):
        if task_id not in visited:
            cycle = visit(task_id)
            if cycle:
                return cycle
    return sorted(remaining)


def plan_execution(payload: object, max_concurrency: int | None = None) -> dict[str, Any]:
    """Validate a task graph and return an ordered sequence of safe execution stages."""
    if not isinstance(payload, dict):
        raise PlanError("plan must be a JSON object")
    if payload.get("schema_version", 1) != 1:
        raise PlanError("schema_version must be 1")
    raw_tasks = payload.get("tasks")
    if not isinstance(raw_tasks, list) or not raw_tasks:
        raise PlanError("tasks must be a non-empty array")

    concurrency = max_concurrency if max_concurrency is not None else payload.get("max_concurrency", 1)
    if not isinstance(concurrency, int) or isinstance(concurrency, bool) or concurrency < 1:
        raise PlanError("max_concurrency must be a positive integer")

    tasks: dict[str, dict[str, Any]] = {}
    for index, raw_task in enumerate(raw_tasks):
        context = f"tasks[{index}]"
        if not isinstance(raw_task, dict):
            raise PlanError(f"{context} must be an object")
        task_id = _require_text(raw_task.get("id"), f"{context}.id")
        if task_id in tasks:
            raise PlanError(f"duplicate task id: {task_id}")
        write_paths = [
            _owned_path(path, f"{context}.write_paths")
            for path in _text_list(raw_task.get("write_paths"), f"{context}.write_paths")
        ]
        tasks[task_id] = {
            "id": task_id,
            "dependencies": _text_list(raw_task.get("dependencies"), f"{context}.dependencies"),
            "write_paths": sorted(set(write_paths)),
            "shared_surfaces": _text_list(
                raw_task.get("shared_surfaces"), f"{context}.shared_surfaces"
            ),
        }

    for task_id, task in tasks.items():
        for dependency in task["dependencies"]:
            if dependency == task_id:
                raise PlanError(f"task {task_id} cannot depend on itself")
            if dependency not in tasks:
                raise PlanError(f"task {task_id} has unknown dependency: {dependency}")

    pair_conflicts: dict[tuple[str, str], list[dict[str, str]]] = {}
    task_ids = sorted(tasks)
    for left_index, left_id in enumerate(task_ids):
        for right_id in task_ids[left_index + 1 :]:
            conflicts = _pair_conflicts(tasks[left_id], tasks[right_id])
            if conflicts:
                pair_conflicts[(left_id, right_id)] = conflicts

    completed: set[str] = set()
    remaining = set(tasks)
    stages: list[dict[str, Any]] = []
    while remaining:
        ready = sorted(
            task_id
            for task_id in remaining
            if set(tasks[task_id]["dependencies"]) <= completed
        )
        if not ready:
            cycle = _find_cycle(tasks, remaining)
            raise PlanError("dependency cycle detected: " + " -> ".join(cycle))

        conflict_degree = {
            task_id: sum(
                bool(pair_conflicts.get(tuple(sorted((task_id, other_id)))))
                for other_id in ready
                if other_id != task_id
            )
            for task_id in ready
        }
        planning_order = sorted(ready, key=lambda task_id: (conflict_degree[task_id], task_id))
        selected: list[str] = []
        deferred: list[dict[str, Any]] = []
        for task_id in planning_order:
            if len(selected) >= concurrency:
                deferred.append({"task_id": task_id, "reason": "max_concurrency"})
                continue
            blocking: list[dict[str, Any]] = []
            for selected_id in selected:
                key = tuple(sorted((task_id, selected_id)))
                conflicts = pair_conflicts.get(key, [])
                if conflicts:
                    blocking.append({"task_id": selected_id, "conflicts": conflicts})
            if blocking:
                deferred.append(
                    {"task_id": task_id, "reason": "ownership_conflict", "blocked_by": blocking}
                )
            else:
                selected.append(task_id)

        selected.sort()
        deferred.sort(key=lambda item: item["task_id"])
        stage_number = len(stages) + 1
        stages.append(
            {
                "id": f"STAGE-{stage_number:03d}",
                "mode": "parallel" if len(selected) > 1 else "sequential",
                "task_ids": selected,
                "ready_task_ids": ready,
                "deferred": deferred,
            }
        )
        completed.update(selected)
        remaining.difference_update(selected)

    conflicts_output = [
        {"task_ids": list(pair), "conflicts": conflicts}
        for pair, conflicts in sorted(pair_conflicts.items())
    ]
    return {
        "schema_version": 1,
        "max_concurrency": concurrency,
        "task_count": len(tasks),
        "stage_count": len(stages),
        "parallel_stage_count": sum(stage["mode"] == "parallel" for stage in stages),
        "stages": stages,
        "conflicts": conflicts_output,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", nargs="?", help="JSON plan path; omit or use - for stdin")
    parser.add_argument("--max-concurrency", type=int, help="override the plan concurrency limit")
    args = parser.parse_args()
    try:
        if args.plan and args.plan != "-":
            with open(args.plan, encoding="utf-8") as handle:
                payload = json.load(handle)
        else:
            payload = json.load(sys.stdin)
        result = plan_execution(payload, args.max_concurrency)
    except (OSError, json.JSONDecodeError, PlanError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
