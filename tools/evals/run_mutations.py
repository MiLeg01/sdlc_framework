#!/usr/bin/env python3
"""Run temporary harmful methodology mutations in isolated repository copies."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evals" / "mutations" / "methodology-cases.json"


def copy_repository(destination: Path) -> None:
    shutil.copytree(
        ROOT,
        destination,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "output", ".DS_Store"),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=CASES)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    cases_path = args.cases if args.cases.is_absolute() else ROOT / args.cases
    cases = json.loads(cases_path.read_text(encoding="utf-8"))["cases"]
    results = []
    for case in cases:
        with tempfile.TemporaryDirectory(prefix="agent-commons-mutation-") as temporary:
            checkout = Path(temporary) / "repository"
            copy_repository(checkout)
            target = checkout / case["target"]
            source = target.read_text(encoding="utf-8")
            count = source.count(case["search"])
            if count != 1:
                results.append({
                    "id": case["id"], "critical": case["critical"], "status": "ERROR",
                    "reason": f"mutation search matched {count} times",
                })
                continue
            target.write_text(source.replace(case["search"], case["replacement"], 1), encoding="utf-8")
            detector = [str(value) for value in case["detector"]]
            if detector and detector[0] == "python3":
                detector[0] = sys.executable
            completed = subprocess.run(
                detector,
                cwd=checkout,
                capture_output=True,
                text=True,
            )
            detector_output = (completed.stdout or "") + (completed.stderr or "")
            expected_failure = str(case["expected_failure"])
            if completed.returncode == 0:
                status = "SURVIVED"
            elif expected_failure in detector_output:
                status = "DETECTED"
            else:
                status = "ERROR"
            results.append({
                "id": case["id"],
                "critical": case["critical"],
                "status": status,
                "detector_exit_code": completed.returncode,
                "expected_failure": expected_failure,
                "detector_output": detector_output[-4000:],
            })
    total = len(results)
    evaluated = [item for item in results if item["status"] in {"DETECTED", "SURVIVED"}]
    detected = sum(item["status"] == "DETECTED" for item in results)
    critical_survivors = [
        item["id"] for item in results
        if item.get("critical") and item["status"] == "SURVIVED"
    ]
    infrastructure_errors = [item["id"] for item in results if item["status"] == "ERROR"]
    payload = {
        "schema_version": 1,
        "total_harmful_mutations": total,
        "evaluated_harmful_mutations": len(evaluated),
        "detected_harmful_mutations": detected,
        "mutation_score": detected / len(evaluated) if evaluated else "not_available",
        "critical_survivors": critical_survivors,
        "infrastructure_errors": infrastructure_errors,
        "status": (
            "PASS"
            if not infrastructure_errors and detected == len(evaluated) and not critical_survivors
            else "FAIL"
        ),
        "results": results,
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "mutation_score": payload["mutation_score"],
        "detected": detected,
        "evaluated": len(evaluated),
        "total": total,
        "infrastructure_errors": len(infrastructure_errors),
    }))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
