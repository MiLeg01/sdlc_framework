#!/usr/bin/env python3
"""Executable trace graph audit evaluations."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRAPH_SCRIPT = ROOT / "skills" / "audit-delivery-traceability" / "scripts" / "audit_trace_graph.py"
CSV_SCRIPT = ROOT / "skills" / "audit-delivery-traceability" / "scripts" / "audit_trace_matrix.py"
FIXTURES = ROOT / "evals" / "fixtures"


class TraceGraphAuditScenarios(unittest.TestCase):
    def run_graph(self, fixture: str, expected_returncode: int) -> dict[str, object]:
        result = subprocess.run(
            ["python3", str(GRAPH_SCRIPT), str(FIXTURES / fixture)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, expected_returncode, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_valid_graph_passes(self) -> None:
        result = self.run_graph("trace-graph-valid.json", 0)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["findings"], [])

    def test_honest_early_lifecycle_passes(self) -> None:
        result = self.run_graph("trace-graph-early-valid.json", 0)
        self.assertEqual(result["status"], "PASS")

    def test_asymmetric_edge_fails(self) -> None:
        result = self.run_graph("trace-graph-asymmetric.json", 1)
        self.assertIn("MISSING_RECIPROCAL", {item["code"] for item in result["findings"]})

    def test_lifecycle_gap_fails(self) -> None:
        result = self.run_graph("trace-graph-lifecycle-gap.json", 1)
        self.assertIn("LIFECYCLE_GAP", {item["code"] for item in result["findings"]})

    def test_stale_generated_view_fails(self) -> None:
        result = self.run_graph("trace-graph-stale-view.json", 1)
        self.assertIn("STALE_GENERATED_VIEW", {item["code"] for item in result["findings"]})

    def test_missing_endpoint_fails(self) -> None:
        result = self.run_graph("trace-graph-missing-endpoint.json", 1)
        self.assertIn("MISSING_ENDPOINT", {item["code"] for item in result["findings"]})

    def test_duplicate_node_id_fails(self) -> None:
        result = self.run_graph("trace-graph-duplicate-id.json", 1)
        self.assertIn("DUPLICATE_NODE_ID", {item["code"] for item in result["findings"]})

    def test_markdown_output_is_supported(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(GRAPH_SCRIPT),
                str(FIXTURES / "trace-graph-valid.json"),
                "--format",
                "markdown",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Status: **PASS**", result.stdout)

    def test_existing_csv_auditor_remains_compatible(self) -> None:
        valid = subprocess.run(
            ["python3", str(CSV_SCRIPT), str(FIXTURES / "trace-valid.csv")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        invalid = subprocess.run(
            ["python3", str(CSV_SCRIPT), str(FIXTURES / "trace-invalid.csv")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
        self.assertNotEqual(invalid.returncode, 0)


if __name__ == "__main__":
    unittest.main()
