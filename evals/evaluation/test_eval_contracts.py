#!/usr/bin/env python3
"""Static contract checks for the canonical evaluation architecture."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "evals"))

from eval_common import load_capability_contracts, load_thresholds, load_workflows, validate_configuration  # noqa: E402
from run_evals import HARD_FAIL, classify_assertion_failures  # noqa: E402


PRIORITY_CAPABILITIES = {
    "initialize-project",
    "continue-project",
    "analyze-legacy-system",
    "inventory-codebase",
    "coordinate-parallel-agents",
    "maintain-project-memory",
    "derive-modernization-requirements",
    "specify-openspec-change",
    "implement-ready-slice",
    "test-driven-development",
    "build-living-dashboard",
    "create-branded-html-artifact",
    "review-for-commons",
    "promote-to-commons",
}

WORKFLOW_CAPABILITIES = {
    "estimate-adm-modernization",
    "deep-research",
    "sales-storytelling",
    "validate-visual-artifact",
    "verify-openspec-implementation",
    "update-commons-presentation",
}


class EvalContractTests(unittest.TestCase):
    def test_configuration_is_internally_consistent(self) -> None:
        self.assertEqual(validate_configuration(), [])

    def test_priority_capabilities_and_all_agents_have_behavior_contracts(self) -> None:
        contracts = load_capability_contracts()["capabilities"]
        agent_ids = {path.stem for path in (ROOT / "agents").glob("*.yaml")}

        self.assertTrue(PRIORITY_CAPABILITIES | WORKFLOW_CAPABILITIES <= set(contracts))
        self.assertTrue(agent_ids <= set(contracts))
        for identifier in PRIORITY_CAPABILITIES | agent_ids:
            scenarios = contracts[identifier]["scenarios"]
            self.assertTrue(any(item["level"] == 2 for item in scenarios), identifier)
            self.assertTrue(any(item["execution"]["kind"] == "external" for item in scenarios), identifier)

        for identifier in WORKFLOW_CAPABILITIES:
            self.assertTrue(any(item["execution"]["kind"] == "external" for item in contracts[identifier]["scenarios"]))

    def test_four_evaluation_levels_and_initial_workflows_exist(self) -> None:
        contracts = load_capability_contracts()["capabilities"]
        workflows = load_workflows()["workflows"]
        levels = {
            scenario["level"]
            for contract in contracts.values()
            for scenario in contract["scenarios"]
        } | {
            scenario["level"]
            for workflow in workflows.values()
            for scenario in workflow["scenarios"]
        }

        self.assertEqual(levels, {1, 2, 3, 4})
        self.assertEqual(
            set(workflows),
            {
                "legacy-modernization",
                "development-delivery",
                "research-presentation",
                "dashboard-quality",
                "public-sector-delivery",
                "commons-governance",
            },
        )

    def test_thresholds_distinguish_quality_cost_and_visual_metrics(self) -> None:
        metrics = load_thresholds()["metrics"]

        self.assertEqual(metrics["runtime"]["warning_increase_percent"], 20.0)
        self.assertEqual(metrics["token_context_efficiency"]["warning_increase_percent"], 20.0)
        self.assertIn("fail_increase_percent", metrics["runtime"])
        self.assertIn("recall", metrics)
        self.assertIn("minimum", metrics["correctness"])
        self.assertIn("minimum", metrics["visual_quality"])

    def test_governance_requires_own_dependent_and_e2e_quality_without_cost_tradeoff(self) -> None:
        governance = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("OWN BEHAVIOR + DEPENDENTS + E2E WORKFLOW", governance)
        self.assertIn("cannot be justified solely by lower runtime or token use", governance)

    def test_golden_files_store_semantics_not_complete_markdown(self) -> None:
        for path in sorted((ROOT / "evals" / "golden").glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            for identifier, expectation in data.items():
                if identifier == "schema_version":
                    continue
                self.assertIsInstance(expectation, dict)
                self.assertNotIn("expected_markdown", expectation)
                self.assertTrue(expectation.get("expected_facts") or expectation.get("required_sequence"))
                self.assertTrue(expectation.get("invariants"))

    def test_required_hard_fail_mutations_are_registered(self) -> None:
        data = json.loads(
            (ROOT / "evals" / "mutations" / "hard-fail-cases.json").read_text(encoding="utf-8")
        )
        assertions = {case["assertion"] for case in data["cases"]}

        self.assertTrue({
            "source_unchanged",
            "critical_expected_behavior",
            "evidence_valid",
            "output_schema_valid",
            "required_dashboard_domains_present",
            "red_evidence_present",
            "evidence_required",
            "ownership_preserved",
            "zero_unaccounted_relevant_sources",
            "canonical_contract_valid",
        } <= assertions)
        self.assertTrue(all(case["expected_status"] == "HARD_FAIL" for case in data["cases"]))

    def test_registered_mutations_drive_hard_failure_classification(self) -> None:
        data = json.loads(
            (ROOT / "evals" / "mutations" / "hard-fail-cases.json").read_text(encoding="utf-8")
        )

        for case in data["cases"]:
            with self.subTest(case=case["id"]):
                self.assertEqual(
                    classify_assertion_failures({case["assertion"]}, {}),
                    HARD_FAIL,
                )

    def test_governance_semantic_fixtures_make_required_evidence_and_tools_explicit(self) -> None:
        scenarios = json.loads(
            (ROOT / "evals/fixtures/evaluation/scenarios.json").read_text(encoding="utf-8")
        )

        self.assertTrue(any(
            "research question" in constraint.lower() and "evidence plan" in constraint.lower()
            for constraint in scenarios["deep-research"]["constraints"]
        ))
        self.assertTrue(any(
            "Do not invent or rename source IDs" in constraint
            for constraint in scenarios["deep-research"]["constraints"]
        ))
        self.assertTrue(any(
            "empty assumption arrays" in constraint
            for constraint in scenarios["estimate-adm-modernization"]["constraints"]
        ))
        self.assertTrue(any(
            "do not invent generic missing assumptions" in constraint.lower()
            for constraint in scenarios["estimate-adm-modernization"]["constraints"]
        ))
        self.assertTrue(any(
            "one evidence_id" in constraint
            for constraint in scenarios["estimate-adm-modernization"]["constraints"]
        ))
        self.assertTrue(any(
            "classification and comparison" in constraint
            for constraint in scenarios["review-for-commons"]["constraints"]
        ))
        self.assertEqual(
            scenarios["review-for-commons"]["workspace_policy"]["writable_artifacts"],
            ["docs/commons-review.md", "docs/commons-review.json"],
        )
        self.assertTrue(any(
            "only the listed writable" in constraint.lower()
            for constraint in scenarios["promote-to-commons"]["constraints"]
        ))
        self.assertTrue(any(
            "exact source-artifact json pointer" in constraint.lower()
            and "directly supports the full observation" in constraint.lower()
            for constraint in scenarios["promote-to-commons"]["constraints"]
        ))
        self.assertTrue(any(
            "observed workspace diff" in constraint.lower()
            and "do not report workspace dependencies as changed" in constraint.lower()
            for constraint in scenarios["promote-to-commons"]["constraints"]
        ))
        for identifier in ("promote-to-commons", "update-commons-presentation"):
            dependencies = scenarios[identifier].get("workspace_dependencies", [])
            self.assertIn("tools", dependencies)
            self.assertIn("install", dependencies)
            self.assertFalse(any("golden" in dependency for dependency in dependencies))

        estimate = json.loads(
            (ROOT / "evals/fixtures/adm-estimation/valid-package.json").read_text(encoding="utf-8")
        )
        self.assertTrue(estimate["scenario"]["assumptions"])
        self.assertTrue(all(unit["assumptions"] for unit in estimate["units"]))

    def test_presentation_refresh_scenarios_may_write_every_file_the_refresh_produces(self) -> None:
        """A scenario told to run the refresh must be allowed to write everything it regenerates."""
        import re

        sync = (ROOT / "tools/sync_presentation.py").read_text(encoding="utf-8")
        constants = {
            name: "/".join(re.findall(r'"([^"]+)"', parts))
            for name, parts in re.findall(r"^([A-Z_]+) = ROOT / (.+)$", sync, re.M)
        }
        produced = {
            constants[name]
            for name in re.findall(r"write_atomic\(([A-Z_]+),", sync)
            if name in constants
        }
        self.assertIn("presentation/agent-commons.html", produced)
        self.assertIn("presentation/assets/library-data.js", produced)

        scenarios = json.loads(
            (ROOT / "evals/fixtures/evaluation/scenarios.json").read_text(encoding="utf-8")
        )
        for identifier, scenario in scenarios.items():
            if not isinstance(scenario, dict):
                continue
            commands = " ".join(str(value) for value in (scenario.get("inputs") or {}).values())
            if "refresh_commons_presentation.py" not in commands:
                continue
            policy = scenario.get("workspace_policy") or {}
            allowed = set(policy.get("writable_artifacts") or [])
            prefixes = tuple(policy.get("generated_prefixes") or ())
            for path in sorted(produced):
                with self.subTest(scenario=identifier, path=path):
                    self.assertTrue(
                        path in allowed or (prefixes and path.startswith(prefixes)),
                        f"{identifier} runs the presentation refresh but cannot write {path}",
                    )


if __name__ == "__main__":
    unittest.main()
