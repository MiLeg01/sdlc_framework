#!/usr/bin/env python3

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

PROMOTIONS = {
    "accessibility-review": "skills",
    "design-test-strategy": "skills",
    "execute-safe-change": "skills",
    "frontend-design": "skills",
    "plan-work": "skills",
    "protect-git-work": "skills",
    "review-code-change": "skills",
    "review-privacy-security": "skills",
    "test-driven-development": "skills",
    "privacy-security-reviewer": "agents",
    "test-behavior-reviewer": "agents",
    "extract-legacy-structure": "tools",
}

MANUAL_REVIEW = ["evidence-backed-performance-validation"]

SELECTED_REVIEW_PROMOTIONS = {
    "anonymize-data": "skills",
    "design-frontend-architecture": "skills",
    "coordinate-parallel-agents": "skills",
    "migrate-code-with-evidence": "skills",
    "architecture-reviewer": "agents",
    "anonymize-structured-data": "tools",
    "validate-migration-manifest": "tools",
}


class CompletenessPromotionTraceabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads((ROOT / "catalog" / "capabilities.yaml").read_text())
        cls.interfaces = json.loads((ROOT / "adapters" / "codex" / "skill-interfaces.yaml").read_text())["interfaces"]
        cls.skill_evals = (ROOT / "evals" / "skills" / "scenarios.yaml").read_text()
        cls.agent_evals = (ROOT / "evals" / "agents" / "scenarios.yaml").read_text()
        cls.archetypes = "\n".join(path.read_text() for path in (ROOT / "archetypes").rglob("*.yaml"))

    def test_exactly_twelve_promotions_resolve_to_canonical_paths(self) -> None:
        self.assertEqual(12, len(PROMOTIONS))
        for capability, kind in PROMOTIONS.items():
            entry = self.catalog[kind][capability]
            self.assertTrue((ROOT / entry["path"]).is_file(), capability)

    def test_each_capability_has_evaluation_coverage(self) -> None:
        for capability, kind in PROMOTIONS.items():
            if kind == "skills":
                self.assertIn(f"  {capability}:", self.skill_evals)
            elif kind == "agents":
                self.assertIn(f"  {capability}:", self.agent_evals)
            else:
                self.assertTrue((ROOT / "evals" / "tools" / "test_legacy_structure_extractor.py").is_file())

    def test_promotions_are_exposed_through_adapters_and_archetypes(self) -> None:
        for capability, kind in PROMOTIONS.items():
            if kind == "skills":
                self.assertIn(capability, self.interfaces)
            self.assertIn(f'"{capability}"', self.archetypes)

    def test_merge_decisions_are_composed_not_duplicated(self) -> None:
        implementation = (ROOT / "skills" / "implement-ready-slice" / "SKILL.md").read_text()
        memory = (ROOT / "skills" / "maintain-project-memory" / "SKILL.md").read_text()
        agents = set(self.catalog["agents"])
        self.assertIn("test-driven-development", implementation)
        self.assertIn("test-behavior-reviewer", implementation)
        self.assertIn("early valid artifact", implementation)
        self.assertIn("earliest valid", memory)
        self.assertFalse(any("frontend" in agent or "accessibility" in agent or "tdd-worker" in agent for agent in agents))

    def test_unselected_manual_review_item_is_not_cataloged(self) -> None:
        all_ids = {identifier for kind in self.catalog["capability_kinds"] for identifier in self.catalog[kind]}
        self.assertTrue(all(identifier not in all_ids for identifier in MANUAL_REVIEW))

    def test_explicitly_selected_review_items_are_traced(self) -> None:
        for capability, kind in SELECTED_REVIEW_PROMOTIONS.items():
            entry = self.catalog[kind][capability]
            self.assertTrue((ROOT / entry["path"]).is_file(), capability)
            self.assertIn(f'"{capability}"', self.archetypes)
            if kind == "skills":
                self.assertIn(capability, self.interfaces)
                self.assertIn(f"  {capability}:", self.skill_evals)
            elif kind == "agents":
                self.assertIn(f"  {capability}:", self.agent_evals)

    def test_attachment_analysis_is_merged_into_research(self) -> None:
        deep_research = (ROOT / "skills" / "deep-research" / "SKILL.md").read_text()
        attachment_reference = ROOT / "skills" / "deep-research" / "references" / "attachment-intake.md"
        self.assertIn("references/attachment-intake.md", deep_research)
        self.assertTrue(attachment_reference.is_file())
        self.assertNotIn("attachment-analysis", self.catalog["skills"])


if __name__ == "__main__":
    unittest.main()
