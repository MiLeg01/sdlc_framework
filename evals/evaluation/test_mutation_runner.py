#!/usr/bin/env python3
"""Mutation testing acceptance checks for critical methodology contracts."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "tools" / "evals" / "run_mutations.py"
CASES = ROOT / "evals" / "mutations" / "methodology-cases.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MutationRunnerTests(unittest.TestCase):
    def test_harmful_mutations_are_temporary_detected_and_scored(self) -> None:
        cases = json.loads(CASES.read_text(encoding="utf-8"))["cases"]
        before = {case["target"]: digest(ROOT / case["target"]) for case in cases}

        with tempfile.TemporaryDirectory() as temporary:
            report = Path(temporary) / "mutation-report.json"
            completed = subprocess.run(
                ["python3", str(RUNNER), "--output", str(report)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            payload = json.loads(report.read_text(encoding="utf-8"))

        self.assertEqual(payload["detected_harmful_mutations"], payload["total_harmful_mutations"])
        self.assertEqual(payload["mutation_score"], 1.0)
        self.assertFalse(payload["critical_survivors"])
        self.assertFalse(payload["infrastructure_errors"])
        self.assertTrue(all(item["status"] == "DETECTED" for item in payload["results"]))
        self.assertEqual(before, {case["target"]: digest(ROOT / case["target"]) for case in cases})

    def test_infrastructure_errors_do_not_reduce_the_mutation_score_or_become_survivors(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cases = root / "cases.json"
            cases.write_text(json.dumps({"cases": [{
                "id": "detector-crash",
                "target": "AGENTS.md",
                "search": "this text deliberately does not exist",
                "replacement": "replacement",
                "critical": True,
                "detector": ["python3", "tools/validate_commons.py"],
                "expected_failure": "expected detector failure",
            }]}), encoding="utf-8")
            report = root / "mutation-report.json"

            completed = subprocess.run(
                ["python3", str(RUNNER), "--cases", str(cases), "--output", str(report)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            payload = json.loads(report.read_text(encoding="utf-8"))

        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["evaluated_harmful_mutations"], 0)
        self.assertEqual(payload["mutation_score"], "not_available")
        self.assertEqual(payload["critical_survivors"], [])
        self.assertEqual(payload["infrastructure_errors"], ["detector-crash"])


if __name__ == "__main__":
    unittest.main()
