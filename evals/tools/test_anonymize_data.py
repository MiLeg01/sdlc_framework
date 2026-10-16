#!/usr/bin/env python3

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "anonymize-data" / "scripts" / "anonymize_data.py"
FIXTURES = ROOT / "evals" / "fixtures" / "anonymization"


class AnonymizeDataTest(unittest.TestCase):
    def test_structured_values_are_masked_deterministically_without_report_leakage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "masked.json"
            report = Path(directory) / "report.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(FIXTURES / "records.json"),
                    str(FIXTURES / "rules.json"),
                    "--output",
                    str(output),
                    "--key-file",
                    str(FIXTURES / "test-key.txt"),
                    "--report",
                    str(report),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            masked = json.loads(output.read_text())
            rendered_report = report.read_text()
            self.assertEqual(masked[0]["email"], masked[1]["email"])
            self.assertTrue(masked[0]["email"].startswith("EMAIL_"))
            self.assertEqual("[REDACTED]", masked[0]["customer_id"])
            self.assertNotIn("Ada", json.dumps(masked))
            self.assertNotIn("ada@example.test", rendered_report)
            self.assertEqual(6, json.loads(rendered_report)["totalMatches"])
            self.assertEqual("ok", json.loads(result.stdout)["status"])

    def test_dry_run_does_not_write_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "masked.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(FIXTURES / "records.json"),
                    str(FIXTURES / "rules.json"),
                    "--output",
                    str(output),
                    "--key-file",
                    str(FIXTURES / "test-key.txt"),
                    "--dry-run",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertFalse(output.exists())
            self.assertEqual("dry-run", json.loads(result.stdout)["status"])

    def test_required_rule_with_no_match_fails_closed(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(FIXTURES / "records.json"),
                str(FIXTURES / "missing-required-rule.json"),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("required rule tax-id matched 0 values", result.stderr)

    def test_csv_and_jsonl_use_the_same_field_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for name in ("records.csv", "records.jsonl"):
                output = Path(directory) / f"masked-{name}"
                subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        str(FIXTURES / name),
                        str(FIXTURES / "rules.json"),
                        "--output",
                        str(output),
                        "--key-file",
                        str(FIXTURES / "test-key.txt"),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                rendered = output.read_text()
                self.assertNotIn("Ada", rendered)
                self.assertNotIn("ada@example.test", rendered)
                self.assertIn("EMAIL_", rendered)

    def test_report_collision_fails_before_any_output_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "masked.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(FIXTURES / "records.json"),
                    str(FIXTURES / "rules.json"),
                    "--output",
                    str(output),
                    "--report",
                    str(output),
                    "--key-file",
                    str(FIXTURES / "test-key.txt"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(2, result.returncode)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
