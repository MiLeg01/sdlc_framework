#!/usr/bin/env python3
"""Acceptance tests for the representative Golden project portfolio."""

from __future__ import annotations

import json
import hashlib
import struct
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROJECTS = ROOT / "evals" / "fixtures" / "projects"


class BenchmarkPortfolioTests(unittest.TestCase):
    def load(self, relative: str) -> dict:
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))

    def test_small_high_value_project_portfolio_is_registered(self) -> None:
        index = self.load("evals/fixtures/projects/index.json")

        self.assertEqual(
            set(index["projects"]),
            {
                "legacy-modernization",
                "development-delivery",
                "research-corpus",
                "dashboard-quality",
                "public-sector-delivery",
            },
        )
        self.assertGreaterEqual(len(index["projects"]), 4)
        self.assertLessEqual(len(index["projects"]), 6)

    def test_each_project_separates_executor_input_from_validator_golden(self) -> None:
        index = self.load("evals/fixtures/projects/index.json")

        for identifier, entry in index["projects"].items():
            with self.subTest(project=identifier):
                fixture = self.load(entry["fixture"])
                golden = self.load(entry["golden"])
                self.assertIn("/input/", entry["fixture"])
                self.assertIn("/golden/", entry["golden"])
                self.assertTrue(fixture["source_artifacts"])
                self.assertTrue(golden["expected_facts"] or golden.get("required_sequence"))
                self.assertTrue(all("/golden/" not in path for path in fixture["source_artifacts"]))

    def test_legacy_project_covers_mixed_language_and_delivery_domains(self) -> None:
        fixture = self.load(
            "evals/fixtures/projects/legacy-modernization/input/scenario.json"
        )
        suffixes = {Path(path).suffix for path in fixture["source_artifacts"]}

        self.assertTrue({".cbl", ".pli", ".java", ".yaml", ".gradle"} <= suffixes)
        self.assertTrue(
            {
                "contracts",
                "runtime-build",
                "requirements",
                "complexity",
                "estimation",
                "roadmap",
                "dashboard",
            }
            <= set(fixture["inputs"]["required_outputs"])
        )

    def test_legacy_project_requires_generated_evidence_ids_to_resolve(self) -> None:
        fixture = self.load(
            "evals/fixtures/projects/legacy-modernization/input/scenario.json"
        )

        self.assertTrue(any(
            "Every evidence identifier cited inside any generated output"
            in item
            and "top-level evidence registry"
            in item
            for item in fixture["constraints"]
        ))

    def test_legacy_project_bounds_the_semantic_result_to_eight_findings(self) -> None:
        fixture = self.load(
            "evals/fixtures/projects/legacy-modernization/input/scenario.json"
        )

        self.assertTrue(any(
            "exactly eight generated_result.observations" in item
            and "Do not add a ninth observation" in item
            for item in fixture["constraints"]
        ))

    def test_development_project_requires_complete_tdd_sequence(self) -> None:
        golden = self.load(
            "evals/fixtures/projects/development-delivery/golden/expectations.json"
        )

        self.assertEqual(
            golden["required_sequence"],
            ["requirement", "specification", "acceptance-criteria", "red", "green", "refactor", "validation"],
        )

    def test_requirement_derivation_preserves_existing_trace_graph_identity(self) -> None:
        scenarios = self.load("evals/fixtures/evaluation/scenarios.json")
        scenario = scenarios["derive-modernization-requirements"]
        constraints = scenario["constraints"]

        self.assertTrue(
            any("existing requirement and specification IDs" in item for item in constraints)
        )
        self.assertTrue(
            any("approved lifecycle states" in item for item in constraints)
        )
        self.assertTrue(
            any("missing-response retry behavior" in item for item in constraints)
        )
        self.assertEqual(scenario["inputs"]["new_requirement_id"], "REQ-SYN-HOST-002")
        self.assertEqual(
            scenario["inputs"]["existing_trace_ids"],
            ["REQ-001", "SPEC-001"],
        )
        self.assertEqual(
            scenario["inputs"]["evidence_set"],
            "evals/fixtures/evaluation/synthetic-modernization-evidence.json",
        )
        evidence = self.load(scenario["inputs"]["evidence_set"])
        self.assertEqual(len(evidence["evidence"]), 4)
        self.assertTrue(
            any("Every factual statement" in item for item in constraints)
        )
        self.assertIn(
            "Use this exact non-factual summary sentence: Modernization requirements derived; see the cited observations below.",
            constraints,
        )
        self.assertTrue(any("Do not invent revision hashes" in item for item in constraints))
        self.assertTrue(any("single factual statement" in item for item in constraints))

    def test_project_initialization_records_preexisting_workspace_inspection(self) -> None:
        scenarios = self.load("evals/fixtures/evaluation/scenarios.json")
        constraints = scenarios["initialize-project"]["constraints"]

        self.assertTrue(
            any("Inspect the pre-existing workspace" in item for item in constraints)
        )
        self.assertTrue(
            any("inspection evidence" in item for item in constraints)
        )

    def test_project_memory_update_is_bounded_to_cited_fixture_facts(self) -> None:
        scenarios = self.load("evals/fixtures/evaluation/scenarios.json")
        constraints = scenarios["maintain-project-memory"]["constraints"]

        self.assertTrue(any(
            "exactly three evidence-backed observations" in item
            for item in constraints
        ))
        self.assertTrue(any(
            "MEM-SYN-001" in item
            and "/records/0/source_fingerprint" in item
            and "/current_sources/0/fingerprint" in item
            for item in constraints
        ))
        self.assertTrue(any(
            "/exclusions" in item
            and "/write_contract" in item
            for item in constraints
        ))

    def test_project_continuation_returns_a_concrete_invalid_reference_action(self) -> None:
        scenarios = self.load("evals/fixtures/evaluation/scenarios.json")
        constraints = scenarios["continue-project"]["constraints"]

        self.assertIn(
            "State the supplied lifecycle state exactly once as: Project lifecycle state: initialized.",
            constraints,
        )
        self.assertTrue(any(
            "REQ-SYN-001 is absent" in item
            and "Do not substitute another item" in item
            and "exactly one concrete next action" in item
            for item in constraints
        ))

    def test_branded_artifact_keeps_every_factual_claim_explicitly_grounded(self) -> None:
        scenarios = self.load("evals/fixtures/evaluation/scenarios.json")
        scenario = scenarios["create-branded-html-artifact"]
        constraints = scenario["constraints"]

        self.assertIn(
            "evals/fixtures/branding/branded-evaluation-template.html",
            scenario["source_artifacts"],
        )
        self.assertIn(
            "skills/create-branded-html-artifact/scripts/render_branded_html.py",
            scenario["source_artifacts"],
        )
        self.assertIn(
            "skills/build-living-dashboard/scripts/brand_profile.py",
            scenario["source_artifacts"],
        )
        self.assertIn(
            "evals/fixtures/branding/render_and_capture_brand_qa.mjs",
            scenario["source_artifacts"],
        )
        self.assertIn(
            "render_and_capture_brand_qa.mjs",
            scenario["inputs"]["browser_command"],
        )
        self.assertIn("branded-evaluation-template.html", scenario["inputs"]["browser_command"])
        self.assertNotIn("render_command", scenario["inputs"])
        self.assertNotIn("static_validation_command", scenario["inputs"])

        self.assertTrue(any(
            "only factual service claim" in item
            and "E-SYN-002" in item
            and "same visible claim block" in item
            for item in constraints
        ))
        self.assertTrue(any(
            "Do not add uncited factual claims" in item
            for item in constraints
        ))
        self.assertTrue(any(
            "exactly two generated_result.observations" in item
            and "Do not add a third observation" in item
            for item in constraints
        ))
        self.assertTrue(any(
            "#/assets/favicon" in item
            and "#/assets/logo" in item
            and "#/evidence" in item
            for item in constraints
        ))
        self.assertTrue(any(
            "artifact/brand-qa.json" in item
            and "Do not predict or claim" in item
            and "trusted runner" in item
            for item in constraints
        ))

    def test_openspec_specification_keeps_equality_boundary_as_a_blocker(self) -> None:
        scenarios = self.load("evals/fixtures/evaluation/scenarios.json")
        constraints = scenarios["specify-openspec-change"]["constraints"]

        self.assertTrue(any(
            "equality boundary" in item
            and "explicit blocker to approval and implementation" in item
            and "do not place it outside the change" in item.lower()
            for item in constraints
        ))

    def test_openspec_verification_requires_exact_evidence_for_each_conclusion(self) -> None:
        scenarios = self.load("evals/fixtures/evaluation/scenarios.json")
        constraints = scenarios["verify-openspec-implementation"]["constraints"]

        self.assertTrue(
            any("exact source artifact path" in item for item in constraints)
        )
        self.assertTrue(
            any("observed test execution" in item for item in constraints)
        )
        self.assertTrue(
            any("uncited conclusions" in item for item in constraints)
        )
        self.assertTrue(any("Every summary sentence" in item for item in constraints))
        self.assertTrue(any("Do not invent revision" in item for item in constraints))
        self.assertTrue(any("exactly six observations" in item for item in constraints))
        self.assertEqual(
            set(scenarios["verify-openspec-implementation"]["workspace_policy"]["writable_artifacts"]),
            {"verification-command-result.txt", "verification-findings.txt"},
        )

    def test_architecture_review_is_bounded_to_supplied_risks(self) -> None:
        scenarios = self.load("evals/fixtures/evaluation/scenarios.json")
        constraints = scenarios["architecture-reviewer"]["constraints"]

        self.assertTrue(any("only the evidenced risks" in item for item in constraints))
        self.assertTrue(any("Do not propose a replacement architecture" in item for item in constraints))
        self.assertTrue(any("exact source path and line locator" in item for item in constraints))
        self.assertTrue(any("Every factual sentence" in item for item in constraints))
        self.assertTrue(any("exactly six severity-ranked findings" in item for item in constraints))
        self.assertTrue(any(
            "CRITICAL shared-schema ownership" in item
            for item in constraints
        ))

    def test_privacy_review_is_bounded_to_three_evidence_backed_findings(self) -> None:
        scenarios = self.load("evals/fixtures/evaluation/scenarios.json")
        constraints = scenarios["privacy-security-reviewer"]["constraints"]

        self.assertTrue(any("exactly three severity-ranked findings" in item for item in constraints))
        self.assertTrue(any("exact source artifact path and JSON pointer" in item for item in constraints))
        self.assertTrue(any(
            "TB-2" in item
            and "/trust_boundaries/1" in item
            and "/flows/2" in item
            for item in constraints
        ))
        self.assertTrue(any(
            "full_request_body" in item
            and "/flows/1" in item
            and "/stores/1" in item
            for item in constraints
        ))
        self.assertTrue(any(
            "export consent basis" in item
            and "/unknowns/0" in item
            and "/unknowns/1" in item
            for item in constraints
        ))
        self.assertTrue(any("Do not claim certification" in item for item in constraints))

    def test_behavior_review_uses_a_non_factual_summary(self) -> None:
        scenarios = self.load("evals/fixtures/evaluation/scenarios.json")
        constraints = scenarios["test-behavior-reviewer"]["constraints"]

        self.assertIn(
            "Use this exact non-factual summary sentence: Test behavior review complete; see the three cited observations below.",
            constraints,
        )

    def test_sales_storytelling_does_not_promote_benefits_beyond_evidence(self) -> None:
        scenarios = self.load("evals/fixtures/evaluation/scenarios.json")
        constraints = scenarios["sales-storytelling"]["constraints"]

        self.assertTrue(any("only proven outcome" in item for item in constraints))
        self.assertTrue(any("audit uncertainty" in item for item in constraints))
        self.assertTrue(any("exact evidence path and line locator" in item for item in constraints))
        self.assertTrue(any("exactly three evidence-backed narrative claims" in item for item in constraints))
        self.assertIn(
            "Use this exact non-factual summary sentence: Sales narrative complete; see the three cited claims below.",
            constraints,
        )
        self.assertTrue(any(
            "third observation" in item
            and "Approve a bounded discovery and validation pilot" in item
            and "Do not add a separate closing line" in item
            for item in constraints
        ))

    def test_estimation_scenario_declares_its_generated_summary(self) -> None:
        scenarios = self.load("evals/fixtures/evaluation/scenarios.json")
        scenario = scenarios["estimate-adm-modernization"]

        self.assertEqual(
            scenario["inputs"]["output"],
            "outputs/adm-estimate-summary.json",
        )
        self.assertIn(
            "outputs/adm-estimate-summary.json",
            scenario["workspace_policy"]["writable_artifacts"],
        )

    def test_commons_governance_requires_complete_sequence_and_invariant_reporting(self) -> None:
        scenarios = self.load("evals/fixtures/evaluation/scenarios.json")
        constraints = scenarios["commons-governance"]["constraints"]

        self.assertTrue(any("exact order" in item for item in constraints))
        self.assertTrue(any("all four invariants" in item for item in constraints))
        self.assertTrue(any("Return only a numbered six-step workflow" in item for item in constraints))
        self.assertTrue(any(
            "synthetic-release-verification as a sibling" in item
            and "unique mapping keys" in item
            for item in constraints
        ))

    def test_public_sector_delivery_has_rendering_assets_and_exact_visual_contract(self) -> None:
        fixture = self.load("evals/fixtures/projects/public-sector-delivery/input/scenario.json")

        self.assertTrue(
            {
                "skills/create-branded-html-artifact/assets/editorial-shell.html",
                "skills/create-branded-html-artifact/scripts/render_branded_html.py",
                "skills/build-living-dashboard/assets/dashboard-shell.html",
                "skills/localize-client-artifact/assets/bilingual-runtime.js",
            }
            <= set(fixture["workspace_dependencies"])
        )
        self.assertEqual(
            fixture["inputs"]["dashboard_shell"],
            "skills/build-living-dashboard/assets/dashboard-shell.html",
        )
        self.assertEqual(
            fixture["inputs"]["presentation_template"],
            "skills/create-branded-html-artifact/assets/editorial-shell.html",
        )
        self.assertTrue(
            any("complete standalone HTML artifacts" in item for item in fixture["constraints"])
        )
        self.assertTrue(
            any("browser manifests and screenshots" in item for item in fixture["constraints"])
        )
        self.assertTrue(any(
            "#overview, #application-map, #requirements, #modernization, and #detail-dialog"
            in item
            for item in fixture["constraints"]
        ))
        self.assertTrue(any(
            "documentElement.scrollWidth never exceeds clientWidth" in item
            for item in fixture["constraints"]
        ))
        self.assertTrue(any(
            "mobile navigation links" in item
            for item in fixture["constraints"]
        ))
        self.assertTrue(any(
            "APP-LEGACY-01, API, Backend, Java, and rev-1" in item
            and "exact literal values" in item
            for item in fixture["constraints"]
        ))
        self.assertTrue(any(
            "preserve every data-canonical-section, data-dashboard-hook, and data-dashboard-region element"
            in item
            for item in fixture["constraints"]
        ))
        self.assertTrue(any(
            "console_errors and overflow_sources are empty" in item
            for item in fixture["constraints"]
        ))
        self.assertTrue(any(
            "data-localization-locale" in item
            and "data-locale" in item
            for item in fixture["constraints"]
        ))
        self.assertTrue(any(
            "All generated files, including temporary and helper scripts" in item
            and "under delivery/" in item
            and "build_artifacts.py" in item
            for item in fixture["constraints"]
        ))
        self.assertTrue(any(
            "first element matching [data-open], [aria-haspopup=dialog]" in item
            and "390" in item
            and "detailDialog.open" in item
            for item in fixture["constraints"]
        ))
        self.assertTrue(any(
            "exactly five generated_result.observations" in item
            and "Do not add a sixth observation" in item
            for item in fixture["constraints"]
        ))
        self.assertTrue(any(
            "public-sector-composition" in item
            and "dashboard-de-default" in item
            and "flag-only-switch" in item
            and "german-sales" in item
            and "safe-branding" in item
            for item in fixture["constraints"]
        ))
        self.assertEqual(
            fixture["inputs"]["sales_presentation"]["document_title"],
            "Nachweisbasierte Modernisierung im öffentlichen Sektor",
        )
        self.assertEqual(fixture["inputs"]["presentation_copy"]["print_button"], "Drucken")
        self.assertTrue(any(
            "html lang attribute to de-AT" in item
            and "exact German title" in item
            and "Remove every remaining Replace with placeholder" in item
            for item in fixture["constraints"]
        ))
        self.assertTrue(any(
            "Use the supplied presentation_copy values exactly" in item
            and "one focused executive composition" in item
            for item in fixture["constraints"]
        ))
        self.assertTrue(any(
            "only as a complete standalone value for de-AT" in item
            and "No other localization key or value" in item
            and "protected literal as a substring" in item
            for item in fixture["constraints"]
        ))
        self.assertTrue(any(
            "Use the exact five claim texts from the golden contract" in item
            and "The sales presentation is German-only." in item
            for item in fixture["constraints"]
        ))

    def test_dashboard_quality_visual_states_target_distinct_sections(self) -> None:
        fixture = self.load("evals/fixtures/projects/dashboard-quality/input/visual-states.json")
        selectors = {state["id"]: state.get("selector") for state in fixture["states"]}

        self.assertEqual(selectors["dashboard-overview"], "#overview")
        self.assertEqual(selectors["dashboard-architecture"], "#application-map")
        self.assertEqual(selectors["dashboard-requirements"], "#requirements")
        self.assertEqual(selectors["dashboard-estimation"], "#modernization")
        self.assertEqual(selectors["dashboard-detail-opener"], "#detail-dialog")
        self.assertEqual(selectors["dashboard-mobile"], "#overview")

    def test_dashboard_quality_result_is_bounded_to_four_golden_observations(self) -> None:
        fixture = self.load("evals/fixtures/projects/dashboard-quality/input/scenario.json")

        self.assertTrue(any(
            "exactly four generated_result.observations" in item
            and "Do not add a fifth observation" in item
            for item in fixture["constraints"]
        ))
        self.assertTrue(any(
            "all-state-domains" in item
            and "test-quality-domain" in item
            and "read-only" in item
            and "representative-visuals" in item
            for item in fixture["constraints"]
        ))

    def test_research_project_uses_local_citable_corpus(self) -> None:
        fixture = self.load("evals/fixtures/projects/research-corpus/input/scenario.json")

        self.assertGreaterEqual(len(fixture["source_artifacts"]), 3)
        self.assertTrue(all(path.endswith(".md") for path in fixture["source_artifacts"]))
        self.assertEqual(fixture["constraints"][0], "Use only the supplied local corpus")
        self.assertTrue(any(
            "exactly eight generated_result.observations" in item
            and "retained for thirty days" in item
            for item in fixture["constraints"]
        ))
        self.assertTrue(any(
            "recommendation-inference" in item
            and "all three supplied notes" in item
            and "Do not repeat" in item
            for item in fixture["constraints"]
        ))

    def test_dashboard_and_public_sector_known_contracts_are_explicit(self) -> None:
        dashboard = self.load("evals/fixtures/projects/dashboard-quality/input/project-state.json")
        public = self.load("evals/fixtures/projects/public-sector-delivery/input/scenario.json")

        self.assertEqual(dashboard["schema_version"], 2)
        self.assertTrue(
            {"requirements", "specifications", "acceptance_criteria", "tests", "evidence", "relationships"}
            <= set(dashboard)
        )
        self.assertTrue(
            {"composition", "inventory", "complexity", "questions", "architecture", "adm_estimate", "roadmap", "test_quality"}
            <= set(dashboard["project"])
        )
        self.assertEqual(public["inputs"]["dashboard"]["default_language"], "de-AT")
        self.assertEqual(public["inputs"]["dashboard"]["switch_labels"], ["🇦🇹", "🇬🇧"])
        self.assertEqual(public["inputs"]["sales_presentation"]["languages"], ["de-AT"])
        self.assertEqual(
            public["inputs"]["protected_technical_literals"],
            ["APP-LEGACY-01", "API", "Backend", "Java", "rev-1"],
        )
        self.assertTrue(any(
            "localization dictionary or message map" in item
            and " · Österreich" in item
            and "no additional characters" in item
            for item in public["constraints"]
        ))

    def test_legacy_analysis_scenario_forbids_spurious_inventory_hash_findings(self) -> None:
        scenarios = self.load("evals/fixtures/evaluation/scenarios.json")
        constraints = scenarios["analyze-legacy-system"]["constraints"]

        self.assertTrue(any(
            "Do not report an inventory hash mismatch" in item
            for item in constraints
        ))
        self.assertTrue(any(
            "exactly six evidence-backed observations" in item
            for item in constraints
        ))

    def test_visual_regression_manifest_has_required_states_and_real_images(self) -> None:
        manifest = self.load("evals/fixtures/visual-regression/manifest.json")
        required = {
            "dashboard-overview",
            "dashboard-architecture",
            "dashboard-requirements",
            "dashboard-estimation",
            "dashboard-detail-opener",
            "dashboard-mobile",
            "presentation-opening",
            "presentation-concepts",
            "presentation-graph",
            "presentation-navigator",
            "presentation-technical",
            "presentation-closing",
        }

        states = {state["id"]: state for state in manifest["states"]}
        self.assertTrue(required <= set(states))
        self.assertFalse(manifest["comparison_policy"]["pixel_equality_required"])
        self.assertLessEqual(manifest["comparison_policy"]["perceptual_difference_threshold"], 0.01)
        for identifier in required:
            screenshot = ROOT / states[identifier]["screenshot"]
            self.assertTrue(screenshot.is_file(), identifier)
            self.assertGreater(screenshot.stat().st_size, 1000, identifier)
            header = screenshot.read_bytes()[:24]
            self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n", identifier)
            width, height = struct.unpack(">II", header[16:24])
            self.assertGreaterEqual(width, 390, identifier)
            self.assertGreaterEqual(height, 600, identifier)
            self.assertEqual(states[identifier]["captured_dimensions"], [width, height])
            self.assertEqual(
                states[identifier]["sha256"], hashlib.sha256(screenshot.read_bytes()).hexdigest(),
            )
            self.assertTrue(states[identifier]["structural_invariants"])


if __name__ == "__main__":
    unittest.main()
