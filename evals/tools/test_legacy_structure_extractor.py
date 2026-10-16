#!/usr/bin/env python3

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "analyze-legacy-system" / "scripts" / "extract_legacy_structure.py"
FIXTURES = ROOT / "evals" / "fixtures" / "legacy-structure"


class LegacyStructureExtractorTest(unittest.TestCase):
    def run_extractor(self, name: str) -> dict:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(FIXTURES / name)],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)["files"][0]

    def test_cobol_preserves_static_and_dynamic_calls_without_comments(self) -> None:
        result = self.run_extractor("sample.cbl")
        observations = {(item["kind"], item["name"]) for item in result["observations"]}
        unresolved = {(item["kind"], item["expression"]) for item in result["unresolved"]}
        self.assertIn(("program", "SAMPLE"), observations)
        self.assertIn(("static-call", "STATIC-PROG"), observations)
        self.assertIn(("dynamic-call", "WS-DYNAMIC-PROG"), unresolved)
        self.assertNotIn(("static-call", "COMMENTED-PROG"), observations)

    def test_java_reports_structure_and_reflection(self) -> None:
        result = self.run_extractor("Sample.java")
        observations = {(item["kind"], item["name"]) for item in result["observations"]}
        self.assertIn(("type", "Sample"), observations)
        self.assertIn(("constructor-call", "Worker"), observations)
        self.assertIn(("qualified-call", "service.execute"), observations)
        self.assertTrue(any(item["kind"] == "reflection-class" for item in result["unresolved"]))
        self.assertFalse(any(item.get("name") == "ignored.call" for item in result["observations"]))

    def test_sql_reports_reads_writes_and_dynamic_sql(self) -> None:
        result = self.run_extractor("sample.sql")
        observations = {(item["kind"], item["name"]) for item in result["observations"]}
        self.assertIn(("routine", "refresh_data"), observations)
        self.assertIn(("table-write", "app.target_table"), observations)
        self.assertIn(("table-read", "app.source_table"), observations)
        self.assertNotIn(("table-write", "ignored_table"), observations)
        self.assertTrue(any(item["kind"] == "dynamic-sql" for item in result["unresolved"]))


if __name__ == "__main__":
    unittest.main()
