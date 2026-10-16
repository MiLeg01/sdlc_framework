#!/usr/bin/env python3
"""Behavioral tests for dependency-aware evaluation selection."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SELECTOR = ROOT / "tools" / "evals" / "select_impacted_evals.py"


class ImpactSelectorTests(unittest.TestCase):
    def select(self, *paths: str) -> dict[str, object]:
        command = ["python3", str(SELECTOR)]
        for path in paths:
            command.extend(["--changed-file", path])
        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)

    def test_memory_change_selects_related_capabilities_and_workflows(self) -> None:
        selected = self.select("skills/maintain-project-memory/scripts/manage_project_memory.py")

        self.assertEqual(selected["changed_capabilities"], ["maintain-project-memory"])
        self.assertTrue(
            {"continue-project", "analyze-legacy-system", "coordinate-parallel-agents"}
            <= set(selected["direct_dependents"])
        )
        self.assertIn("legacy-modernization", selected["workflows"])
        self.assertIn("development-delivery", selected["workflows"])
        self.assertIn("maintain-project-memory:behavior", selected["required_scenarios"])

    def test_catalog_change_selects_every_contract(self) -> None:
        selected = self.select("catalog/capabilities.yaml")

        self.assertTrue(selected["all_capabilities"])
        self.assertIn("initialize-project", selected["changed_capabilities"])
        self.assertIn("commons-governance", selected["workflows"])

    def test_golden_change_is_reported_as_protected(self) -> None:
        selected = self.select("evals/golden/critical-capabilities.json")

        self.assertEqual(
            selected["protected_changes"],
            ["evals/golden/critical-capabilities.json"],
        )
        self.assertIn("initialize-project", selected["changed_capabilities"])
        self.assertTrue(selected["required_scenarios"])

    def test_threshold_change_selects_every_contract(self) -> None:
        selected = self.select("evals/contracts/thresholds.json")

        self.assertTrue(selected["all_capabilities"])
        self.assertIn("commons-governance", selected["workflows"])

    def test_hard_fail_registry_change_is_protected_and_selects_every_contract(self) -> None:
        selected = self.select("evals/mutations/hard-fail-cases.json")

        self.assertTrue(selected["all_capabilities"])
        self.assertEqual(selected["protected_changes"], ["evals/mutations/hard-fail-cases.json"])
        self.assertIn("commons-governance", selected["workflows"])

    def test_workflow_golden_change_selects_workflow(self) -> None:
        selected = self.select("evals/golden/workflows.json")

        self.assertEqual(
            set(selected["workflows"]),
            {"commons-governance"},
        )

    def test_project_golden_change_is_protected_and_selects_its_workflow(self) -> None:
        path = "evals/fixtures/projects/legacy-modernization/golden/expectations.json"
        selected = self.select(path)

        self.assertEqual(selected["protected_changes"], [path])
        self.assertIn("legacy-modernization", selected["workflows"])

    def test_hidden_directory_name_is_not_stripped(self) -> None:
        selected = self.select(".github/workflows/evals.yml")

        self.assertEqual(selected["changed_files"], [".github/workflows/evals.yml"])

    def test_archetype_change_selects_representative_workflow(self) -> None:
        selected = self.select("archetypes/legacy-migration/archetype.yaml")

        self.assertEqual(selected["changed_archetypes"], ["legacy-migration"])
        self.assertIn("legacy-modernization", selected["workflows"])

    def test_uncontracted_canonical_capability_is_reported(self) -> None:
        selected = self.select("skills/review-code-change/SKILL.md")

        self.assertEqual(selected["uncovered_changed_capabilities"], ["review-code-change"])

    def test_capability_id_input_selects_dependencies_without_a_file_path(self) -> None:
        completed = subprocess.run(
            ["python3", str(SELECTOR), "--capability", "maintain-project-memory"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        selected = json.loads(completed.stdout)

        self.assertEqual(selected["requested_capability_ids"], ["maintain-project-memory"])
        self.assertEqual(selected["changed_capabilities"], ["maintain-project-memory"])
        self.assertIn("legacy-modernization", selected["workflows"])


if __name__ == "__main__":
    unittest.main()
