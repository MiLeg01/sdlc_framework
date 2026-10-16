#!/usr/bin/env python3
"""Validate portable ADM estimate invariants and emit deterministic totals."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def load_package(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("package root must be an object")
    return value


def summarize(package: dict) -> tuple[dict, list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    units = package.get("units")
    if not isinstance(units, list):
        return {}, ["units must be an array"]

    scenario = package.get("scenario")
    if not isinstance(scenario, dict):
        errors.append("scenario must be an object")
        scenario = {}
    if scenario.get("unit") != "person-days":
        errors.append("scenario.unit must be person-days")
    if not scenario.get("targetArchitecture"):
        warnings.append("target architecture is not declared")
    if not scenario.get("deliveryModel"):
        warnings.append("delivery model is not declared")

    seen: set[str] = set()
    totals = {"optimistic": 0.0, "mostLikely": 0.0, "pessimistic": 0.0, "expected": 0.0}
    workstreams: dict[str, dict[str, float]] = defaultdict(
        lambda: {"optimistic": 0.0, "mostLikely": 0.0, "pessimistic": 0.0, "expected": 0.0}
    )
    estimated_count = 0
    unestimated: list[str] = []
    unit_results: list[dict] = []

    for index, unit in enumerate(units):
        if not isinstance(unit, dict):
            errors.append(f"units[{index}] must be an object")
            continue
        unit_id = unit.get("id")
        if not isinstance(unit_id, str) or not unit_id:
            errors.append(f"units[{index}].id is required")
            continue
        if unit_id in seen:
            errors.append(f"duplicate unit ID: {unit_id}")
        seen.add(unit_id)

        trace_ids = unit.get("traceIds")
        if not isinstance(trace_ids, list) or not trace_ids:
            warnings.append(f"{unit_id}: no canonical traceability")
        unknown_dimensions = sorted({
            str(driver.get("dimension", "UNNAMED")).strip() or "UNNAMED"
            for driver in unit.get("complexityDrivers", [])
            if isinstance(driver, dict) and driver.get("rating") == "UNKNOWN"
        })
        if unknown_dimensions:
            warnings.append(f"{unit_id}: unknown complexity drivers: {', '.join(unknown_dimensions)}")

        estimate = unit.get("estimate")
        if estimate is None:
            unestimated.append(unit_id)
            continue
        if not isinstance(estimate, dict):
            errors.append(f"{unit_id}: estimate must be an object or null")
            continue
        try:
            optimistic = float(estimate["optimistic"])
            likely = float(estimate["mostLikely"])
            pessimistic = float(estimate["pessimistic"])
        except (KeyError, TypeError, ValueError):
            errors.append(f"{unit_id}: estimate values must be numeric")
            continue
        if optimistic < 0 or not optimistic <= likely <= pessimistic:
            errors.append(f"{unit_id}: expected 0 <= optimistic <= mostLikely <= pessimistic")
            continue

        expected = (optimistic + 4 * likely + pessimistic) / 6
        result = {
            "id": unit_id,
            "workstream": unit.get("workstream", "UNASSIGNED"),
            "optimistic": round(optimistic, 2),
            "mostLikely": round(likely, 2),
            "pessimistic": round(pessimistic, 2),
            "expected": round(expected, 2),
        }
        unit_results.append(result)
        estimated_count += 1
        for key in totals:
            totals[key] += result[key]
            workstreams[result["workstream"]][key] += result[key]

    calibration = package.get("calibration")
    if not isinstance(calibration, dict):
        errors.append("calibration must be an object")
        calibration = {}
    if calibration.get("basis") == "UNAVAILABLE":
        warnings.append("calibration is unavailable; treat totals as rough-order-of-magnitude")
        if calibration.get("confidence") != "LOW":
            errors.append("unavailable calibration requires LOW confidence")
    if unestimated:
        warnings.append(f"{len(unestimated)} work unit(s) are unestimated")

    summary = {
        "schemaVersion": "1.0.0",
        "batchId": package.get("batchId"),
        "repositoryFingerprint": package.get("repositoryFingerprint"),
        "unit": "person-days",
        "counts": {"total": len(units), "estimated": estimated_count, "unestimated": len(unestimated)},
        "totals": {key: round(value, 2) for key, value in totals.items()},
        "workstreams": {
            key: {metric: round(value, 2) for metric, value in values.items()}
            for key, values in sorted(workstreams.items())
        },
        "units": unit_results,
        "unestimatedUnitIds": unestimated,
        "warnings": sorted(set(warnings)),
    }
    return summary, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        package = load_package(args.package)
        summary, errors = summarize(package)
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
