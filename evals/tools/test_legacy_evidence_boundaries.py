#!/usr/bin/env python3
"""Regression checks for legacy evidence authority boundaries."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class LegacyEvidenceBoundaryTests(unittest.TestCase):
    def test_test_strategy_requires_explicit_legacy_oracle_authority(self) -> None:
        skill = (ROOT / "skills/design-test-strategy/SKILL.md").read_text(encoding="utf-8")
        reference_path = ROOT / "skills/design-test-strategy/references/legacy-oracle-readiness.md"

        self.assertTrue(reference_path.exists())
        reference = reference_path.read_text(encoding="utf-8")
        for term in (
            "APPROVED_INTENT",
            "OBSERVED_SOURCE",
            "UNRESOLVED",
            "READY_FOR_EXPECTED_OUTCOMES",
            "CHARACTERIZATION_ONLY",
            "SCENARIO_ONLY",
            "REVIEW_REQUIRED",
            "BLOCKED",
        ):
            self.assertIn(term, reference)
        self.assertIn("legacy-oracle-readiness.md", skill)
        self.assertIn("Generated", reference)
        self.assertIn("executed", reference.lower())
        self.assertIn("passed", reference.lower())

    def test_legacy_analysis_keeps_reference_applications_out_of_target_truth(self) -> None:
        skill = (ROOT / "skills/analyze-legacy-system/SKILL.md").read_text(encoding="utf-8")
        reference_path = ROOT / "skills/analyze-legacy-system/references/reference-applications.md"
        archetype = (ROOT / "archetypes/legacy-migration/archetype.yaml").read_text(encoding="utf-8")

        self.assertTrue(reference_path.exists())
        reference = reference_path.read_text(encoding="utf-8")
        self.assertIn("REFERENCE_PATTERN", reference)
        self.assertIn("discovery prior", reference.lower())
        self.assertIn("matches and non-matches", reference.lower())
        self.assertIn("target evidence", reference.lower())
        self.assertIn("reference-applications.md", skill)
        self.assertIn("reference application", archetype.lower())
        self.assertIn("never target evidence", archetype.lower())

    def test_behavior_scenarios_cover_positive_negative_collision_and_regression(self) -> None:
        scenarios = (ROOT / "evals/skills/scenarios.yaml").read_text(encoding="utf-8")
        for scenario_id in (
            "approved_legacy_oracle",
            "generic_generated_outcome",
            "observed_behavior_conflicts_with_intent",
            "ordinary_nonlegacy_strategy",
            "reference_pattern_target_match",
            "reference_only_candidate",
            "reference_pattern_target_nonmatch",
            "analysis_without_reference_profile",
        ):
            self.assertIn(scenario_id, scenarios)

    def test_semantic_fixtures_and_goldens_are_registered(self) -> None:
        contracts = json.loads((ROOT / "evals/contracts/capabilities.json").read_text(encoding="utf-8"))
        fixtures = json.loads((ROOT / "evals/fixtures/evaluation/scenarios.json").read_text(encoding="utf-8"))
        goldens = json.loads((ROOT / "evals/golden/critical-capabilities.json").read_text(encoding="utf-8"))

        self.assertIn("design-test-strategy", contracts["capabilities"])
        self.assertIn("design-test-strategy", fixtures)
        self.assertIn("design-test-strategy", goldens)
        reference_scenarios = {
            item["id"]
            for item in contracts["capabilities"]["analyze-legacy-system"]["scenarios"]
        }
        self.assertIn("reference-prior", reference_scenarios)
        self.assertIn("analyze-legacy-reference-prior", fixtures)
        self.assertIn("analyze-legacy-reference-prior", goldens)


if __name__ == "__main__":
    unittest.main()
