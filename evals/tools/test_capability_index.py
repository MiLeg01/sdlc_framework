#!/usr/bin/env python3
"""Executable checks for the deterministic fast capability index."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "build_capability_index.py"
SPEC = importlib.util.spec_from_file_location("build_capability_index", SCRIPT)
assert SPEC and SPEC.loader
INDEXER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INDEXER)


class CapabilityIndexScenarios(unittest.TestCase):
    def test_committed_index_matches_canonical_sources(self) -> None:
        committed = json.loads((ROOT / "catalog" / "capability-index.json").read_text(encoding="utf-8"))
        self.assertEqual(INDEXER.generate(), committed)

    def test_routing_entry_contains_trigger_boundary_composition_and_runtime(self) -> None:
        entries = {item["id"]: item for item in INDEXER.generate()["capabilities"]}
        parallel = entries["coordinate-parallel-agents"]
        self.assertEqual(parallel["type"], "skill")
        self.assertTrue(parallel["trigger"])
        self.assertIn("Do not use", parallel["non_trigger"])
        self.assertIn("legacy-migration", parallel["archetypes"])
        self.assertIn("development", parallel["archetypes"])
        self.assertIn("codex", parallel["runtime_availability"])


if __name__ == "__main__":
    unittest.main()
