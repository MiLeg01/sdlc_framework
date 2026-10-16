#!/usr/bin/env python3
"""Acceptance checks for the representative project-memory benchmark."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "evals" / "tools" / "benchmark_project_memory.py"


class ProjectMemoryBenchmarkTests(unittest.TestCase):
    def test_mixed_language_resume_reduces_repeated_context_without_depth_regression(self) -> None:
        result = subprocess.run(
            ["python3", str(SCRIPT)], cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["fixture"], "mixed-cobol-pli-java")
        self.assertEqual(payload["measurement"], "UTF-8 bytes")
        self.assertGreaterEqual(payload["context_reduction_percent"], 30)
        self.assertGreater(payload["resume"]["validated_slices_reused"], 0)
        self.assertEqual(payload["resume"]["repeated_unchanged_source_reads"], 0)
        self.assertEqual(payload["depth_quality"]["before"], payload["depth_quality"]["after"])
        self.assertFalse(payload["depth_quality"]["regression"])
        self.assertNotIn("token_count", payload)
        self.assertGreater(payload["performance"]["baseline_runtime_seconds"], 0)
        self.assertGreater(payload["performance"]["optimized_runtime_seconds"], 0)
        self.assertEqual(payload["performance"]["tokens"], "not_available")


if __name__ == "__main__":
    unittest.main()
