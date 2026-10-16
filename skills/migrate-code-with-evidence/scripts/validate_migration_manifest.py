#!/usr/bin/env python3
"""Validate a bounded, traceable, fail-closed code-migration manifest."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any


FORBIDDEN_KEY = re.compile(r"(?:api[_-]?key|password|secret|access[_-]?token|credential)", re.I)
UNSAFE_COMMAND = re.compile(r"(?:\brm\s+-rf\b|\bsudo\b|\bcurl\b[^\n|]*\|\s*(?:sh|bash)\b|\bwget\b[^\n|]*\|\s*(?:sh|bash)\b)", re.I)
STATUSES = {"PLANNED", "RED", "GREEN", "VERIFIED", "BLOCKED"}


def object_at(value: Any, key: str, errors: list[str]) -> dict[str, Any]:
    child = value.get(key) if isinstance(value, dict) else None
    if not isinstance(child, dict):
        errors.append(f"{key} must be an object")
        return {}
    return child


def string_list(value: Any, label: str, errors: list[str], *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty) or not all(isinstance(item, str) and item.strip() for item in value):
        errors.append(f"{label} must be {'a' if allow_empty else 'a non-empty'} string array")
        return []
    return value


def find_forbidden_keys(value: Any, path: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            current = f"{path}.{key}" if path else key
            if FORBIDDEN_KEY.fullmatch(key) and not (path == "safety" and key == "credentials"):
                findings.append(current)
            findings.extend(find_forbidden_keys(child, current))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(find_forbidden_keys(child, f"{path}[{index}]"))
    return findings


def normalized_root(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    return str(PurePosixPath(value.strip()))


def is_nested(child: str, parent: str) -> bool:
    child_parts = PurePosixPath(child).parts
    parent_parts = PurePosixPath(parent).parts
    return len(child_parts) > len(parent_parts) and child_parts[:len(parent_parts)] == parent_parts


def validate(manifest: Any) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return {}, ["manifest root must be an object"]
    if manifest.get("schemaVersion") != "1.0.0":
        errors.append("schemaVersion must be 1.0.0")

    source = object_at(manifest, "source", errors)
    target = object_at(manifest, "target", errors)
    scope = object_at(manifest, "scope", errors)
    safety = object_at(manifest, "safety", errors)
    source_root = normalized_root(source.get("root"))
    target_root = normalized_root(target.get("root"))
    if not source_root:
        errors.append("source.root is required")
    if not target_root:
        errors.append("target.root is required")
    if source_root and source_root == target_root:
        errors.append("source.root and target.root must be distinct")
    if source_root and target_root and is_nested(target_root, source_root):
        errors.append("target.root must not be inside source.root")
    if source_root and ".." in PurePosixPath(source_root).parts:
        errors.append("source.root must not contain parent traversal")
    if target_root and ".." in PurePosixPath(target_root).parts:
        errors.append("target.root must not contain parent traversal")
    if source.get("readOnly") is not True:
        errors.append("source.readOnly must be true")
    for label, obj, key in (("source", source, "language"), ("source", source, "fingerprint"), ("target", target, "language")):
        if not isinstance(obj.get(key), str) or not obj[key].strip():
            errors.append(f"{label}.{key} is required")
    string_list(target.get("constraints"), "target.constraints", errors)
    string_list(scope.get("included"), "scope.included", errors)
    string_list(scope.get("excluded"), "scope.excluded", errors, allow_empty=True)

    expected_safety = {
        "credentials": "external",
        "network": "disabled-by-default",
        "writeBoundary": "isolated-target",
        "humanReviewRequired": True,
    }
    for key, expected in expected_safety.items():
        if safety.get(key) != expected:
            errors.append(f"safety.{key} must be {json.dumps(expected)}")
    for path in find_forbidden_keys(manifest):
        errors.append(f"credential-like key is forbidden: {path}")

    slices = manifest.get("slices")
    if not isinstance(slices, list) or not slices:
        errors.append("slices must be a non-empty array")
        slices = []
    seen: set[str] = set()
    scenario_count = 0
    for index, item in enumerate(slices):
        label = f"slices[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        slice_id = item.get("id")
        if not isinstance(slice_id, str) or not slice_id.strip():
            errors.append(f"{label}.id is required")
            continue
        if slice_id in seen:
            errors.append(f"duplicate slice id: {slice_id}")
        seen.add(slice_id)
        if item.get("status") not in STATUSES:
            errors.append(f"{slice_id}.status must be one of {sorted(STATUSES)}")
        for key in ("sourceArtifacts", "requirements", "acceptanceScenarios", "targetArtifacts", "tests", "validationCommands"):
            values = string_list(item.get(key), f"{slice_id}.{key}", errors)
            if key == "acceptanceScenarios":
                scenario_count += len(values)
            if key == "validationCommands":
                for command in values:
                    if UNSAFE_COMMAND.search(command):
                        errors.append(f"{slice_id}: unsafe validation command: {command}")

    summary = {
        "schemaVersion": "1.0.0",
        "sourceFingerprint": source.get("fingerprint"),
        "sliceCount": len(slices),
        "acceptanceScenarioCount": scenario_count,
        "writeBoundary": safety.get("writeBoundary"),
        "statuses": {status: sum(1 for item in slices if isinstance(item, dict) and item.get("status") == status) for status in sorted(STATUSES)},
    }
    return summary, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        summary, errors = validate(manifest)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 2
    sys.stdout.write(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
