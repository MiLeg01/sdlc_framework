#!/usr/bin/env python3
"""Compare current evaluation performance with the accepted last-green baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from eval_common import ROOT, load_json, load_thresholds
from run_evals import compare_performance_to_baseline


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current", type=Path, required=True, help="Current performance.json")
    parser.add_argument("--baseline", type=Path, default=ROOT / "evals/baselines/v1.0.0.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    current_path = args.current if args.current.is_absolute() else ROOT / args.current
    baseline_path = args.baseline if args.baseline.is_absolute() else ROOT / args.baseline
    current = json.loads(current_path.read_text(encoding="utf-8"))
    if not isinstance(current, list):
        raise SystemExit("current performance must be a JSON array")
    comparison, _ = compare_performance_to_baseline(current, load_json(baseline_path), load_thresholds())
    rendered = json.dumps(comparison, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    if comparison["status"] == "REGRESSION_FAIL":
        return 1
    if comparison["status"] == "NOT_AVAILABLE":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
