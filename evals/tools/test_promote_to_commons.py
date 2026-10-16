from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = ROOT / "skills" / "promote-to-commons"


class PromoteToCommonsContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.contract = (SKILL_DIR / "references" / "promotion-contract.md").read_text(encoding="utf-8")
        self.report = (SKILL_DIR / "references" / "report-contract.md").read_text(encoding="utf-8")
        self.scenarios = (ROOT / "evals" / "skills" / "scenarios.yaml").read_text(encoding="utf-8")
        self.catalog = json.loads((ROOT / "catalog" / "capabilities.yaml").read_text(encoding="utf-8"))
        self.interfaces = json.loads((ROOT / "adapters" / "codex" / "skill-interfaces.yaml").read_text(encoding="utf-8"))

    @staticmethod
    def normalized(text: str) -> str:
        return re.sub(r"\s+", " ", text.lower()).strip()

    def test_explicit_selection_is_a_hard_mutation_gate(self) -> None:
        required = [
            "only an explicit user selection authorizes",
            "Do not mutate anything until the selected set is unambiguous",
            "never infer that a review authorizes every proposal",
            "do not mutate commons",
        ]
        combined = self.normalized(f"{self.skill}\n{self.contract}")
        for phrase in required:
            self.assertIn(self.normalized(phrase), combined)

    def test_revalidation_dispositions_and_artifact_types_are_complete(self) -> None:
        for disposition in [
            "PROMOTE_NEW", "PROMOTE_UPDATE", "PROMOTE_MERGE", "PROMOTE_DEPRECATION",
            "BLOCK_CONFIDENTIAL", "BLOCK_LICENSE", "BLOCK_DUPLICATE",
            "BLOCK_INSUFFICIENT_EVIDENCE", "BLOCK_WRONG_ABSTRACTION", "NEEDS_USER_DECISION",
        ]:
            self.assertIn(disposition, self.contract)
        for artifact in ["Skills", "Agents", "Tools", "Templates, archetypes, and overlays"]:
            self.assertIn(artifact, self.contract)

    def test_external_confidentiality_eval_and_git_controls_are_present(self) -> None:
        combined = self.normalized(f"{self.skill}\n{self.contract}\n{self.report}")
        for phrase in [
            "Unknown or incompatible license blocks copying and adaptation",
            "BLOCK_CONFIDENTIAL",
            "positive, negative, collision",
            "Never make a promotion commit that silently absorbs unrelated work",
            "failed validation",
        ]:
            self.assertIn(self.normalized(phrase), combined)

    def test_all_required_behavioral_scenarios_exist(self) -> None:
        block = self.scenarios.split("  promote-to-commons:\n", 1)[1].split("\n  inventory-codebase:", 1)[0]
        for scenario_id in [
            "a_new_reusable_skill", "b_existing_skill_update", "c_already_covered",
            "d_client_specific", "e_external_valid_license", "f_external_unknown_license",
            "g_ambiguous_selection", "h_select_one_of_many", "i_agent_without_delegation_value",
            "j_routing_collision", "k_validation_failure", "l_tdd_promotion",
        ]:
            self.assertIn(f"      {scenario_id}:", block)

    def test_catalog_and_codex_interface_expose_the_canonical_skill(self) -> None:
        entry = self.catalog["skills"]["promote-to-commons"]
        self.assertEqual(entry["path"], "skills/promote-to-commons/SKILL.md")
        self.assertIn("review-for-commons", entry["related"])
        self.assertIn("promote-to-commons", self.interfaces["interfaces"])

    def test_canonical_skill_is_runtime_neutral_and_reports_are_auditable(self) -> None:
        for path in sorted(SKILL_DIR.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"\$[a-z][a-z0-9-]+", path.as_posix())
            self.assertNotIn(".codex/", text.lower(), path.as_posix())
            self.assertNotRegex(text, r"/Users/", path.as_posix())
        for field in [
            "user-selected and excluded candidates", "per-candidate revalidation summary",
            "confidentiality scan result", "validation commands and exact outcomes", "commit identity",
        ]:
            self.assertIn(field, self.report)


if __name__ == "__main__":
    unittest.main()
