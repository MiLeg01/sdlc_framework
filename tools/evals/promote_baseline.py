#!/usr/bin/env python3
"""Deliberately promote an explicitly accepted green run to last-green baseline."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from eval_common import ROOT, validate_against_schema


def build_capabilities(performance: list[dict]) -> dict:
    grouped: dict[str, list[dict]] = {}
    for item in performance:
        subject, _ = item["scenario"].split(":", 1)
        grouped.setdefault(subject, []).append(item)
    output = {}
    for subject, items in grouped.items():
        metric_names = sorted({name for item in items for name in item.get("metrics_mean", {})})
        output[subject] = {
            "pass_rate": sum(float(item["pass_rate"]) for item in items) / len(items),
            "metrics": {
                name: sum(float(item["metrics_mean"][name]) for item in items if name in item.get("metrics_mean", {}))
                / sum(name in item.get("metrics_mean", {}) for item in items)
                for name in metric_names
            },
            "runtime_seconds": sum(float(item["duration_mean_seconds"]) for item in items),
            "tokens": (
                sum(float(item["tokens_mean"]) for item in items if isinstance(item.get("tokens_mean"), (int, float)))
                if any(isinstance(item.get("tokens_mean"), (int, float)) for item in items)
                else "not_available"
            ),
        }
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--accepted-run", required=True, help="Reviewed pipeline or run identifier")
    parser.add_argument("--branch", help="Accepted branch; defaults to the run summary or current Git branch")
    args = parser.parse_args()

    run_dir = args.run_dir if args.run_dir.is_absolute() else ROOT / args.run_dir
    output = args.output if args.output.is_absolute() else ROOT / args.output
    summary = json.loads((run_dir / "quality-summary.json").read_text(encoding="utf-8"))
    performance = json.loads((run_dir / "performance.json").read_text(encoding="utf-8"))
    recorded_branch = summary.get("selection", {}).get("branch")
    recorded_profile = summary.get("selection", {}).get("profile")
    if not recorded_branch:
        raise SystemExit("quality summary must record the evaluated branch")
    branch = args.branch or recorded_branch
    if recorded_branch != branch:
        raise SystemExit("requested branch does not match the branch recorded by the evaluation run")
    if branch != "main":
        raise SystemExit("last-green promotion is restricted to an explicitly accepted main-branch run")
    if recorded_profile not in {"full", "nightly"}:
        raise SystemExit("last-green promotion requires the recorded full profile")
    counts = summary.get("counts", {})
    if summary.get("status") != "PASS" or any(
        int(counts.get(name, 0)) for name in ("warnings", "regression_failures", "hard_failures")
    ):
        raise SystemExit("last-green promotion requires a fully green run without warnings or regressions")
    baseline = {
        "schema_version": 1,
        "version": "1.0.0",
        "status": "accepted",
        "baseline_commit": summary.get("current_commit"),
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "accepted_run": {
            "id": args.accepted_run,
            "branch": branch,
            "profile": summary.get("selection", {}).get("profile", "not_available"),
        },
        "capabilities": build_capabilities(performance),
        "scenarios": {item["scenario"]: item for item in performance},
    }
    errors = validate_against_schema(baseline, "evals/schemas/last-green-baseline.schema.json")
    if errors:
        raise SystemExit("invalid promoted baseline: " + "; ".join(errors))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
