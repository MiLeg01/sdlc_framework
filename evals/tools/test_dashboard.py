#!/usr/bin/env python3
"""Executable evaluations for the requirements/specifications dashboard."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/build-living-dashboard/scripts/build_dashboard.py"
STRUCTURE_VALIDATOR = ROOT / "skills/build-living-dashboard/scripts/validate_dashboard_structure.py"
SEMANTIC_VALIDATOR = ROOT / "skills/build-living-dashboard/scripts/validate_dashboard_semantics.py"
EXAMPLE = ROOT / "skills/build-living-dashboard/assets/dashboard-data.example.json"
STRUCTURE = ROOT / "skills/build-living-dashboard/assets/dashboard-structure.json"
GOLDEN = ROOT / "evals/fixtures/dashboard/golden-reference-structure.json"
VISUAL_STATES = ROOT / "evals/fixtures/dashboard/visual-reference-states.json"
SPEC = importlib.util.spec_from_file_location("dashboard", SCRIPT)
dashboard = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(dashboard)
import brand_profile

BRAND_PROFILE = ROOT / "evals/fixtures/branding/resolved-public-sector-profile.json"


class DashboardScenarios(unittest.TestCase):
    def data(self) -> dict:
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def brand_profile(self) -> dict:
        return json.loads(BRAND_PROFILE.read_text(encoding="utf-8"))

    def test_many_to_many_traceability_and_full_validation(self) -> None:
        result = dashboard.validate(self.data())
        self.assertEqual(result["requirements"][0]["specification_ids"], ["SPEC-001", "SPEC-002"])
        self.assertEqual(result["specifications"][0]["requirement_ids"], ["REQ-001", "REQ-002"])
        self.assertEqual(result["specifications"][0]["validation_status"], "PASS")
        self.assertEqual(result["requirements"][0]["evidence_ids"], ["EVID-001"])
        self.assertEqual(result["acceptance_criteria"][0]["test_ids"], ["TEST-001"])
        self.assertTrue(any(row["test"] == "TEST-001" for row in result["traceability"]))
        req1_spec1 = [row for row in result["traceability"]
                      if row["requirement"] == "REQ-001" and row["specification"] == "SPEC-001"]
        req2_spec1 = [row for row in result["traceability"]
                      if row["requirement"] == "REQ-002" and row["specification"] == "SPEC-001"]
        self.assertEqual({row["acceptance_criterion"] for row in req1_spec1}, {"AC-001"})
        self.assertEqual({row["acceptance_criterion"] for row in req2_spec1}, {"AC-002"})
        self.assertEqual(req1_spec1[0]["implementation_item"], "SLICE-001")

    def test_conflicting_or_missing_criterion_ownership_fails(self) -> None:
        missing = self.data()
        missing["acceptance_criteria"][0].pop("requirement_id")
        with self.assertRaisesRegex(ValueError, "requires explicit requirement_id"):
            dashboard.validate(missing)
        conflicting = self.data()
        conflicting["acceptance_criteria"][2]["requirement_id"] = "REQ-002"
        with self.assertRaisesRegex(ValueError, "is not linked to specification"):
            dashboard.validate(conflicting)
        compatible = self.data()
        compatible["acceptance_criteria"][2].pop("requirement_id")
        self.assertEqual(dashboard.validate(compatible)["acceptance_criteria"][2]["requirement_id"], "REQ-001")

    def test_actions_derive_from_structured_state_and_render_copy_controls(self) -> None:
        result = dashboard.validate(self.data())
        requirement = next(item for item in result["requirements"] if item["id"] == "REQ-001")
        specification = next(item for item in result["specifications"] if item["id"] == "SPEC-002")
        self.assertEqual(requirement["next_action"]["command"], "$review-openspec-change SPEC-002")
        self.assertEqual(specification["next_action"]["command"], "$review-openspec-change SPEC-002")
        self.assertEqual(result["project"]["next_action"]["command"], "$review-openspec-change SPEC-002")
        shell = (ROOT / "skills/build-living-dashboard/assets/dashboard-shell.html").read_text(encoding="utf-8")
        rendered = dashboard.render(result, shell)
        self.assertIn('data-copy-command="$', rendered)
        self.assertIn("$review-openspec-change SPEC-002", rendered)
        self.assertIn("Kopieren", rendered)

    def test_missing_specification_is_a_gap(self) -> None:
        data = self.data()
        data["relationships"] = [r for r in data["relationships"] if r.get("source") != "REQ-002"]
        data["acceptance_criteria"] = [item for item in data["acceptance_criteria"] if item["requirement_id"] != "REQ-002"]
        data["relationships"] = [r for r in data["relationships"] if r.get("source") != "AC-002" and r.get("target") != "AC-002"]
        result = dashboard.validate(data)
        self.assertIn("APPROVED_REQUIREMENT_UNSPECIFIED", {w["code"] for w in result["warnings"]})

    def test_full_analysis_coverage_is_first_class_and_false_completion_is_rejected(self) -> None:
        data = self.data()
        data["analysis"] = {
            "mode": "CONTINUE", "target_mode": "FULL", "status": "IN-PROGRESS",
            "coverage": {"relevant": 77, "accounted": 52, "unaccounted": 25, "blocked": 0},
            "slices": {"validated": 6, "total": 9},
            "languages": ["COBOL", "PL/I", "Java", "OpenAPI/configuration"],
        }
        result = dashboard.validate(data)
        self.assertEqual(result["metrics"][0]["label"], "Source accounted")
        self.assertEqual(result["metrics"][0]["value"], "52 / 77")
        data["analysis"]["status"] = "COMPLETE"
        with self.assertRaisesRegex(ValueError, "cannot be complete"):
            dashboard.validate(data)

    def test_requirement_revision_makes_specification_stale(self) -> None:
        data = self.data()
        data["requirements"][0]["revision"] = 3
        result = dashboard.validate(data)
        self.assertTrue(result["specifications"][0]["stale"])
        self.assertIn("STALE_SPECIFICATION", {w["code"] for w in result["warnings"]})

    def test_unresolved_criterion_is_not_ready(self) -> None:
        data = self.data()
        data["specifications"][1]["readiness"] = "ready"
        result = dashboard.validate(data)
        self.assertIn("READY_WITH_UNRESOLVED_CRITERIA", {w["code"] for w in result["warnings"]})

    def test_green_test_does_not_cover_an_unlinked_criterion(self) -> None:
        data = self.data()
        data["relationships"] = [r for r in data["relationships"]
                                 if not (r["type"] == "validated-by" and r["source"] == "AC-002")]
        result = dashboard.validate(data)
        self.assertEqual(result["specifications"][0]["validation_status"], "PARTIAL")
        self.assertEqual(result["specifications"][0]["uncovered_acceptance_criterion_ids"], ["AC-002"])

    def test_duplicate_and_missing_endpoints_fail(self) -> None:
        duplicate = self.data()
        duplicate["tests"][0]["id"] = "REQ-001"
        with self.assertRaisesRegex(ValueError, "duplicate lifecycle ID"):
            dashboard.validate(duplicate)
        missing = self.data()
        missing["relationships"][0]["target"] = "SPEC-404"
        with self.assertRaisesRegex(ValueError, "endpoint missing"):
            dashboard.validate(missing)

    def test_render_check_and_interaction_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "index.html"
            subprocess.run(["python3", str(SCRIPT), "--data", str(EXAMPLE), "--output", str(output)], check=True)
            checked = subprocess.run(["python3", str(SCRIPT), "--data", str(EXAMPLE), "--output", str(output), "--check"], capture_output=True, text=True)
            rendered = output.read_text(encoding="utf-8")
            structure = subprocess.run([
                "python3", str(STRUCTURE_VALIDATOR), "--html", str(output),
            ], capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        for marker in ('data-open=', 'data-canonical-section="overview"', 'data-dashboard-hook="detail-dialog"',
                       'Requirements', 'Specifications', 'Traceability'):
            self.assertIn(marker, rendered)
        self.assertEqual(structure.returncode, 0, structure.stdout + structure.stderr)
        self.assertIn("Dashboard structure: PASS", structure.stdout)

    def test_visual_layer_keeps_heading_skip_and_localization_semantics(self) -> None:
        data = dashboard.validate(self.data())
        shell = (ROOT / "skills/build-living-dashboard/assets/dashboard-shell.html").read_text(encoding="utf-8")
        rendered = dashboard.render(data, shell)
        for marker in (
            '<h1 id="project-title">',
            '<main id="main" tabindex="-1">',
            'data-i18n="classification.core"',
            'data-i18n="group.overview.label"',
            'placeholder:ui.search_placeholder',
            '@media(max-width:400px)',
        ):
            self.assertIn(marker, rendered)
        self.assertIn("Lifecycle QA pending", rendered)
        self.assertNotIn('id="validation-state" data-i18n="dashboard.status.validated"', rendered)

    def test_large_registers_have_bounded_accessible_controls(self) -> None:
        data = self.data()
        data["evidence"] = [
            {"id": f"EVID-{index:03d}", "title": f"Synthetic evidence {index}", "kind": "source",
             "location": f"synthetic/file-{index}.txt:{index}", "summary": "Synthetic record"}
            for index in range(150)
        ]
        data["relationships"] = [relation for relation in data["relationships"] if relation["type"] != "supported-by"]
        result = dashboard.validate(data)
        result["traceability"] = result["traceability"] * 100
        self.assertEqual(len(result["traceability"]), 300)
        shell = (ROOT / "skills/build-living-dashboard/assets/dashboard-shell.html").read_text(encoding="utf-8")
        rendered = dashboard.render(result, shell)
        self.assertEqual(result["dashboard"]["registers"]["evidence"]["initial_limit"], 25)
        self.assertEqual(result["dashboard"]["registers"]["traceability"]["initial_limit"], 50)
        for marker in ('class="register-summary" role="status" aria-live="polite"',
                       'data-load-more=', 'data-trace-depth', '.slice(0,state.limit)'):
            self.assertIn(marker, rendered)

    def test_project_register_details_are_indexed_and_plain_strings_are_not_fake_links(self) -> None:
        data = self.data()
        data["project"] = {
            "capabilities": [{"id": "CAP-SYNTHETIC", "title": "Synthetic capability", "description": "Detail"}],
            "inventory": ["Plain inventory statement"],
        }
        result = dashboard.validate(data)
        shell = (ROOT / "skills/build-living-dashboard/assets/dashboard-shell.html").read_text(encoding="utf-8")
        rendered = dashboard.render(result, shell)
        self.assertIn("projectRecords=", rendered)
        self.assertIn("item.id&&byId[item.id]", rendered)
        self.assertIn("typeof raw==='string'?{title:raw}:raw", rendered)

    def test_nested_localization_coverage_is_complete_and_fresh(self) -> None:
        data = self.data()
        data["project"] = {"decision_brief": {"recommendation": "Proceed with a synthetic pilot."}}
        data["delivery"] = {"languages": ["de-AT", "en"], "default_language": "de-AT",
                            "language_switch": True, "storage_key": "synthetic-language"}
        provisional = copy.deepcopy(data)
        provisional["delivery"] = {"languages": ["en"], "default_language": "en",
                                   "language_switch": False, "storage_key": "synthetic-language"}
        sources = dashboard.rendered_localization_sources(dashboard.validate(provisional))
        data["localization"] = {"messages": {
            key: {"source": source, "source_hash": "sha256:" + hashlib.sha256(source.encode()).hexdigest(),
                  "translations": {"de-AT": f"Fachlich übersetzter Beispielinhalt {index}."}}
            for index, (key, source) in enumerate(sources.items(), start=1)
        }}
        self.assertEqual(dashboard.validate(copy.deepcopy(data))["localization_coverage"]["status"], "PASS")
        key = "project.decision_brief.recommendation"
        placeholder = copy.deepcopy(data)
        placeholder["localization"]["messages"][key]["translations"]["de-AT"] = "DE: " + placeholder["localization"]["messages"][key]["source"]
        with self.assertRaisesRegex(ValueError, "placeholder translation"):
            dashboard.validate(placeholder)
        identical = copy.deepcopy(data)
        identical["localization"]["messages"][key]["translations"]["de-AT"] = identical["localization"]["messages"][key]["source"]
        with self.assertRaisesRegex(ValueError, "unintentionally identical"):
            dashboard.validate(identical)
        empty = copy.deepcopy(data)
        empty["localization"]["messages"][key]["translations"]["de-AT"] = ""
        with self.assertRaisesRegex(ValueError, "missing translation"):
            dashboard.validate(empty)
        stale = copy.deepcopy(data)
        stale["localization"]["messages"][key]["source_hash"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(ValueError, "stale source hash"):
            dashboard.validate(stale)
        del data["localization"]["messages"][key]
        with self.assertRaisesRegex(ValueError, "project.decision_brief.recommendation"):
            dashboard.validate(data)

    def test_source_data_cannot_claim_dashboard_validated_or_complete(self) -> None:
        for status in ("VALIDATED", "COMPLETE"):
            data = self.data()
            data["dashboard"] = {"status": status}
            with self.assertRaisesRegex(ValueError, "external lifecycle-QA result"):
                dashboard.validate(data)

    def test_language_switch_runtime_preserves_filters_dialog_scroll_and_diagram_state(self) -> None:
        source = (ROOT / "skills/build-living-dashboard/assets/dashboard-shell.html").read_text(encoding="utf-8")
        for invariant in ("captureUiState", "restoreUiState", "scrollTo(...state.scroll)",
                          "detailDialog.dataset.recordId", "data-diagram-state", "registerState",
                          "input.dataset.sectionFilter"):
            self.assertIn(invariant, source)

    def test_austrian_public_sector_dashboard_uses_flag_only_german_english_switch(self) -> None:
        data = self.data()
        data["delivery"] = {"languages": ["de-AT", "en"], "default_language": "de-AT",
                            "language_switch": True, "storage_key": "austrian-public-sector-language"}
        provisional = copy.deepcopy(data)
        provisional["delivery"] = {"languages": ["en"], "default_language": "en",
                                   "language_switch": False, "storage_key": "austrian-public-sector-language"}
        sources = dashboard.rendered_localization_sources(dashboard.validate(provisional))
        data["localization"] = {"messages": {
            key: {"source": source, "source_hash": "sha256:" + hashlib.sha256(source.encode()).hexdigest(),
                  "translations": {"de-AT": f"Fachlich übersetzter Beispielinhalt {index}."}}
            for index, (key, source) in enumerate(sources.items(), start=1)
        }}
        shell = (ROOT / "skills/build-living-dashboard/assets/dashboard-shell.html").read_text(encoding="utf-8")
        rendered = dashboard.render(dashboard.validate(data), shell)
        self.assertIn('data-localization-locale="de-AT"', rendered)
        self.assertIn('aria-label="Deutsch (Österreich)"><span aria-hidden="true">🇦🇹</span>', rendered)
        self.assertIn('data-localization-locale="en"', rendered)
        self.assertIn('aria-label="English"><span aria-hidden="true">🇬🇧</span>', rendered)
        self.assertNotIn('>Deutsch (Österreich)<', rendered)
        self.assertNotIn('>English<', rendered)

    def test_management_layer_preserves_structure_and_progressive_disclosure(self) -> None:
        data = dashboard.validate(self.data())
        data["audience"] = "management"
        shell = (ROOT / "skills/build-living-dashboard/assets/dashboard-shell.html").read_text(encoding="utf-8")
        rendered = dashboard.render(data, shell)
        self.assertLess(rendered.index('data-canonical-section="overview"'),
                        rendered.index('data-canonical-section="requirements"'))
        self.assertIn("Show technical detail", rendered)
        self.assertIn('data-canonical-section="evidence"', rendered)

    def test_canonical_structure_matches_sanitized_golden_reference(self) -> None:
        structure = json.loads(STRUCTURE.read_text(encoding="utf-8"))
        golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
        self.assertEqual([group["id"] for group in structure["navigation"]["groups"]],
                         golden["navigation_groups"])
        self.assertEqual([section["id"] for section in structure["sections"]
                          if section["classification"] == "core"], golden["core_sections"])
        overview = next(section for section in structure["sections"] if section["id"] == "overview")
        self.assertEqual(overview["required_regions"], golden["required_overview_regions"])
        self.assertEqual([point["id"] for point in structure["extension_points"]],
                         golden["required_extension_points"])
        self.assertEqual(structure["navigation"]["model"], golden["reference_patterns"][0])
        self.assertEqual(structure["navigation"]["mobile_model"], golden["reference_patterns"][1])
        self.assertEqual(structure["chrome"], golden["chrome"])

    def test_full_legacy_modernization_structure_uses_the_complete_canonical_order(self) -> None:
        expected = [
            "overview", "decision-brief", "stakeholder-questions", "modernization",
            "capabilities", "requirements", "specifications", "flows",
            "inventory", "database", "interfaces", "dependencies", "external-estate",
            "application-map", "progress", "traceability", "evidence", "test-quality",
            "questions-risks",
        ]
        data = self.data()
        data["dashboard"] = {"mode": "full-legacy-modernization", "extensions": []}
        result = dashboard.validate(data)
        self.assertEqual(
            [section["id"] for section in result["dashboard_structure"]["sections"]], expected,
        )
        self.assertEqual(
            [item["section_ids"] for item in result["dashboard_structure"]["navigation"]],
            [expected[0:4], expected[4:8], expected[8:10], expected[10:14], expected[14:19]],
        )
        self.assertTrue(all(section.get("empty_state") for section in result["dashboard_structure"]["sections"]))

    def test_required_standard_sections_cannot_be_silently_removed(self) -> None:
        data = self.data()
        data["dashboard"] = {"mode": "full-legacy-modernization", "enabled_sections": ["overview"]}
        result = dashboard.validate(data)
        section_ids = [section["id"] for section in result["dashboard_structure"]["sections"]]
        self.assertIn("stakeholder-questions", section_ids)
        self.assertIn("database", section_ids)
        self.assertIn("test-quality", section_ids)
        self.assertIn("questions-risks", section_ids)

    def test_canonical_information_domains_have_stable_locations_and_states(self) -> None:
        data = self.data()
        data["dashboard"] = {"mode": "canonical", "profile": "legacy-modernization"}
        data.setdefault("project", {})["composition"] = {
            "basis": "MEASURED",
            "languages": [
                {"name": "COBOL", "files": 3},
                {"name": "PL/I", "files": 2},
                {"name": "Java", "files": 4},
                {"name": "SQL", "files": 1},
            ],
        }
        result = dashboard.validate(data)
        canonical = json.loads(STRUCTURE.read_text(encoding="utf-8"))["information_domains"]
        domains = result["dashboard_structure"]["information_domains"]
        self.assertEqual([item["id"] for item in domains], [item["id"] for item in canonical])
        self.assertTrue(all(item["status"] in {
            "AVAILABLE", "IN_PROGRESS", "NOT_YET_ANALYZED", "NOT_APPLICABLE", "BLOCKED",
        } for item in domains))
        rendered = dashboard.render(result, (ROOT / "skills/build-living-dashboard/assets/dashboard-shell.html").read_text(encoding="utf-8"))
        for item in canonical:
            self.assertIn(f'data-information-domain="{item["id"]}"', rendered)

    def test_database_free_monolith_no_tests_and_no_specifications_keep_honest_slots(self) -> None:
        data = self.data()
        data["specifications"] = []
        data["acceptance_criteria"] = []
        data["implementation_items"] = []
        data["tests"] = []
        data["relationships"] = [
            relation for relation in data["relationships"]
            if relation["type"] == "supported-by"
        ]
        data["openspec_required"] = True
        data["dashboard"] = {"mode": "canonical", "profile": "legacy-modernization"}
        data.setdefault("project", {}).update({
            "persistence": {"relational_detected": False, "stores": ["VSAM"]},
            "topology": {"current": "monolith"},
            "test_quality": {
                "automated_tests": 0,
                "assessment": "No automated legacy tests detected.",
                "risk": "High characterization-test requirement.",
            },
        })
        result = dashboard.validate(data)
        states = {item["id"]: item for item in result["dashboard_structure"]["information_domains"]}
        self.assertEqual(states["entity-relationship-model"]["status"], "NOT_APPLICABLE")
        self.assertIn("No relational schema", states["entity-relationship-model"]["reason"])
        self.assertEqual(states["service-topology"]["status"], "AVAILABLE")
        self.assertIn("monolith", states["service-topology"]["reason"].lower())
        self.assertEqual(states["legacy-test-quality"]["status"], "AVAILABLE")
        self.assertIn("No automated legacy tests", states["legacy-test-quality"]["reason"])
        self.assertEqual(states["openspec-specifications"]["status"], "NOT_YET_ANALYZED")

    def _test_quality_reason(self, quality: dict) -> str:
        data = self.data()
        data["dashboard"] = {"mode": "canonical", "profile": "legacy-modernization"}
        data.setdefault("project", {})["test_quality"] = quality
        result = dashboard.validate(data)
        states = {item["id"]: item for item in result["dashboard_structure"]["information_domains"]}
        self.assertEqual(states["legacy-test-quality"]["status"], "AVAILABLE")
        return states["legacy-test-quality"]["reason"]

    def test_test_quality_exposes_mutation_metrics_when_they_exist(self) -> None:
        reason = self._test_quality_reason({
            "automated_tests": 142,
            "assessment": "Unit and integration suites are maintained.",
            "mutation": {
                "status": "GOOD",
                "score": 0.88,
                "critical_survivors": 0,
                "surviving_meaningful_mutants": 7,
                "trend": "IMPROVED",
            },
        })
        self.assertIn("Mutation testing: GOOD", reason)
        self.assertIn("88.0%", reason)
        self.assertIn("0 critical survivors", reason)
        self.assertIn("7 meaningful survivors", reason)
        self.assertIn("trend IMPROVED", reason)

    def test_unanalyzed_mutation_state_is_reported_rather_than_omitted(self) -> None:
        reason = self._test_quality_reason({
            "automated_tests": 12,
            "assessment": "Tests pass.",
            "coverage_percent": 100,
        })
        self.assertIn("NOT_YET_ANALYZED", reason)

    def test_unsupported_mutation_tooling_states_its_reason(self) -> None:
        reason = self._test_quality_reason({
            "automated_tests": 4,
            "assessment": "Characterization harness in place.",
            "mutation": {
                "status": "NOT_SUPPORTED",
                "reason": "no maintained mutation engine exists for COBOL; the migrated Java target was assessed instead",
            },
        })
        self.assertIn("NOT_SUPPORTED", reason)
        self.assertIn("COBOL", reason)

    def test_flaky_baseline_blocks_the_test_quality_state(self) -> None:
        reason = self._test_quality_reason({
            "automated_tests": 88,
            "assessment": "Suite is green but unstable.",
            "mutation": {
                "status": "BLOCKED_BY_FLAKY_TESTS",
                "reason": "three repeats produced different failure sets",
            },
        })
        self.assertIn("BLOCKED_BY_FLAKY_TESTS", reason)

    def test_canonical_test_quality_model_keeps_coverage_subordinate_to_mutation(self) -> None:
        model = json.loads(STRUCTURE.read_text(encoding="utf-8"))["test_quality_model"]
        metrics = {item["id"]: item for item in model["metrics"]}
        for identifier in (
            "mutation_score", "killed_mutants", "surviving_meaningful_mutants",
            "critical_survivors", "mutation_trend", "test_quality_status",
        ):
            self.assertIn(identifier, metrics)
        self.assertFalse(metrics["coverage"]["required"])
        self.assertIn("substitute", metrics["coverage"]["note"])
        for state in ("NOT_YET_ANALYZED", "NOT_SUPPORTED", "BLOCKED_BY_FLAKY_TESTS"):
            self.assertIn(state, model["test_quality_states"])
        self.assertIn("surviving mutant", model["drill_down"])
        self.assertIn("mutation operator", model["drill_down"])
        self.assertIn("aggregate", model["management_overview_rule"])
        self.assertTrue(any("methodology mutation" in item for item in model["prohibited"]))

    def test_semantic_validator_fails_when_a_required_domain_is_missing(self) -> None:
        data = self.data()
        data["dashboard"] = {"mode": "canonical", "profile": "legacy-modernization"}
        result = dashboard.validate(data)
        result["dashboard_structure"]["information_domains"] = [
            item for item in result["dashboard_structure"]["information_domains"]
            if item["id"] != "legacy-test-quality"
        ]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "dashboard.json"
            path.write_text(json.dumps(result), encoding="utf-8")
            checked = subprocess.run(
                ["python3", str(SEMANTIC_VALIDATOR), "--data", str(path)],
                capture_output=True, text=True,
            )
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("missing information domains", checked.stdout)

    def test_available_domains_and_completed_modernization_require_supporting_content(self) -> None:
        available = self.data()
        available["dashboard"] = {
            "mode": "canonical", "profile": "legacy-modernization",
            "domain_states": {"complexity": {"status": "AVAILABLE", "basis": "ASSESSED"}},
        }
        with self.assertRaisesRegex(ValueError, "complexity: AVAILABLE has no supporting canonical content"):
            dashboard.validate(available)

        complete = self.data()
        complete["analysis"] = {
            "target_mode": "FULL", "status": "COMPLETE",
            "coverage": {"relevant": 1, "accounted": 1, "unaccounted": 0, "blocked": 0},
        }
        complete["dashboard"] = {"mode": "full-legacy-modernization", "profile": "legacy-modernization"}
        with self.assertRaisesRegex(ValueError, "completed modernization dashboard is missing executive findings"):
            dashboard.validate(complete)

    def test_shared_claims_bind_dashboard_paths_to_visible_peer_markers(self) -> None:
        data = self.data()
        data["dashboard"] = {"shared_claims": [{
            "id": "scope-count", "dashboard_paths": ["title"], "peer_markers": ["77 files"],
        }]}
        result = dashboard.validate(data)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "dashboard.json"
            peer = root / "presentation.html"
            path.write_text(json.dumps(result), encoding="utf-8")
            missing_peer = subprocess.run(
                ["python3", str(SEMANTIC_VALIDATOR), "--data", str(path)],
                capture_output=True, text=True,
            )
            peer.write_text("<html><body><main>76 files</main><script>77 files</script></body></html>", encoding="utf-8")
            hidden_only = subprocess.run(
                ["python3", str(SEMANTIC_VALIDATOR), "--data", str(path), "--peer-html", str(peer)],
                capture_output=True, text=True,
            )
            peer.write_text("<html><body><main>77 files</main></body></html>", encoding="utf-8")
            passing = subprocess.run(
                ["python3", str(SEMANTIC_VALIDATOR), "--data", str(path), "--peer-html", str(peer)],
                capture_output=True, text=True,
            )
        self.assertNotEqual(missing_peer.returncode, 0)
        self.assertIn("require --peer-html", missing_peer.stdout)
        self.assertNotEqual(hidden_only.returncode, 0)
        self.assertIn("peer marker missing", hidden_only.stdout)
        self.assertEqual(passing.returncode, 0, passing.stdout + passing.stderr)

        invalid = self.data()
        invalid["dashboard"] = {"shared_claims": [{
            "id": "missing", "dashboard_paths": ["project.not_there"], "peer_markers": ["marker"],
        }]}
        with self.assertRaisesRegex(ValueError, "empty dashboard paths"):
            dashboard.validate(invalid)

    def test_system_statistics_cannot_be_available_without_measured_inventory_basis(self) -> None:
        data = self.data()
        data["dashboard"] = {"mode": "canonical", "profile": "legacy-modernization"}
        data.setdefault("project", {})["composition"] = {
            "basis": "ASSESSED",
            "languages": [{"name": "Java", "files": 10}],
        }
        with self.assertRaisesRegex(ValueError, "system-statistics must be MEASURED"):
            dashboard.validate(data)

    def test_structure_validator_rejects_a_missing_standard_section_in_full_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "index.html"
            subprocess.run([
                "python3", str(SCRIPT), "--data", str(EXAMPLE), "--output", str(output),
                "--dashboard-mode", "full-legacy-modernization",
            ], check=True, capture_output=True, text=True)
            source = output.read_text(encoding="utf-8")
            source = source.replace(' data-canonical-section="database"', ' data-removed-section="database"', 1)
            output.write_text(source, encoding="utf-8")
            result = subprocess.run([
                "python3", str(STRUCTURE_VALIDATOR), "--html", str(output),
            ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("STRUCTURE_PASS: FAIL", result.stdout)
        self.assertIn("database", result.stdout)

    def test_canonical_mode_keeps_irrelevant_implementation_views_as_explicit_states(self) -> None:
        data = self.data()
        data["specifications"] = []
        data["acceptance_criteria"] = []
        data["implementation_items"] = []
        data["tests"] = []
        data["relationships"] = [relation for relation in data["relationships"]
                                 if relation["type"] == "supported-by"]
        data["openspec_required"] = False
        data["dashboard"] = {"enabled_sections": ["requirements", "inventory"], "extensions": []}
        result = dashboard.validate(data)
        sections = [section["id"] for section in result["dashboard_structure"]["sections"]]
        self.assertIn("requirements", sections)
        self.assertIn("inventory", sections)
        self.assertIn("specifications", sections)
        self.assertIn("modernization", sections)
        states = {item["id"]: item["status"] for item in result["dashboard_structure"]["information_domains"]}
        self.assertIn(states["openspec-specifications"], {"NOT_YET_ANALYZED", "NOT_APPLICABLE"})
        self.assertIn(states["roadmap"], {"NOT_YET_ANALYZED", "NOT_APPLICABLE"})

    def test_project_extensions_are_bounded_and_ordered(self) -> None:
        data = self.data()
        data["dashboard"] = {"enabled_sections": [], "extensions": [{
            "id": "research-findings", "title": "Research findings",
            "extension_point": "business-domain", "summary": "Synthetic findings",
        }]}
        result = dashboard.validate(data)
        sections = result["dashboard_structure"]["sections"]
        extension = next(section for section in sections if section["id"] == "research-findings")
        self.assertEqual(extension["classification"], "project-specific")
        self.assertEqual(extension["order"], 81)
        invalid = self.data()
        invalid["dashboard"] = {"enabled_sections": [], "extensions": [{
            "id": "bad", "title": "Bad", "extension_point": "anywhere", "order": 999,
        }]}
        with self.assertRaisesRegex(ValueError, "unsupported dashboard extension point"):
            dashboard.validate(invalid)

    def test_structural_validator_detects_navigation_drift(self) -> None:
        data = dashboard.validate(self.data())
        shell = (ROOT / "skills/build-living-dashboard/assets/dashboard-shell.html").read_text(encoding="utf-8")
        rendered = dashboard.render(data, shell).replace('data-section-target="overview"',
                                                         'data-section-target="risks"', 1)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "drift.html"
            path.write_text(rendered, encoding="utf-8")
            checked = subprocess.run(["python3", str(STRUCTURE_VALIDATOR), "--html", str(path)],
                                     capture_output=True, text=True)
        self.assertEqual(checked.returncode, 1)
        self.assertIn("navigation order differs", checked.stdout)

    def test_structural_validator_rejects_coordinated_payload_and_markup_drift(self) -> None:
        data = dashboard.validate(self.data())
        sections = data["dashboard_structure"]["sections"]
        sections[0], sections[1] = sections[1], sections[0]
        data["dashboard_structure"]["navigation"][0]["section_ids"] = [sections[0]["id"], sections[1]["id"]]
        shell = (ROOT / "skills/build-living-dashboard/assets/dashboard-shell.html").read_text(encoding="utf-8")
        rendered = dashboard.render(data, shell)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "coordinated-drift.html"
            path.write_text(rendered, encoding="utf-8")
            checked = subprocess.run(["python3", str(STRUCTURE_VALIDATOR), "--html", str(path)],
                                     capture_output=True, text=True)
        self.assertEqual(checked.returncode, 1)
        self.assertIn("resolved section order is outside the canonical order", checked.stdout)

    def test_visual_reference_states_have_stable_selectors_and_mobile_contract(self) -> None:
        data = self.data()
        data["dashboard"] = {"enabled_sections": ["application-map"], "extensions": []}
        result = dashboard.validate(data)
        shell = (ROOT / "skills/build-living-dashboard/assets/dashboard-shell.html").read_text(encoding="utf-8")
        rendered = dashboard.render(result, shell)
        states = json.loads(VISUAL_STATES.read_text(encoding="utf-8"))["states"]
        for state in states:
            selector = state["selector"]
            marker = f'id="{selector[1:]}"' if selector.startswith("#") else selector[1:]
            self.assertIn(marker, rendered)
        self.assertIn("@media(max-width:720px)", rendered)
        self.assertIn("bottom:0;height:3.75rem", rendered)

    def test_brand_variants_keep_identical_information_architecture(self) -> None:
        neutral = dashboard.validate(self.data())
        branded_data = self.data()
        branded_data["brand_profile"] = self.brand_profile()
        branded = dashboard.validate(branded_data)
        self.assertEqual([section["id"] for section in neutral["dashboard_structure"]["sections"]],
                         [section["id"] for section in branded["dashboard_structure"]["sections"]])
        shell = (ROOT / "skills/build-living-dashboard/assets/dashboard-shell.html").read_text(encoding="utf-8")
        self.assertNotEqual(dashboard.render(neutral, shell), dashboard.render(branded, shell))

    def test_evidence_derived_brand_profile_controls_rendered_theme_and_fingerprints(self) -> None:
        data = self.data()
        data["brand_profile"] = self.brand_profile()
        result = dashboard.validate(data)
        shell = (ROOT / "skills/build-living-dashboard/assets/dashboard-shell.html").read_text(encoding="utf-8")
        rendered = dashboard.render(result, shell)
        profile = result["brand_profile"]
        self.assertIn('data-brand-id="synthetic-public-sector"', rendered)
        self.assertIn(f'data-brand-profile-fingerprint="{profile["profile_fingerprint"]}"', rendered)
        self.assertIn("--accent:#006f8b", rendered)
        self.assertIn("--display:Arial Narrow, Arial, sans-serif", rendered)
        self.assertIn(profile["theme_fingerprint"], rendered)
        self.assertEqual(len(result["fingerprint"]), 64)

    def test_required_brand_must_be_resolved_and_cannot_equal_generic_fallback(self) -> None:
        unresolved = self.brand_profile()
        unresolved["status"] = "blocked"
        with self.assertRaisesRegex(ValueError, "required brand profile is not resolved"):
            dashboard.validate_brand_profile(unresolved)

        generic = self.brand_profile()
        generic["theme"] = copy.deepcopy(brand_profile.GENERIC_THEME)
        generic["observed_colors"] = [
            {"value": color, "usages": ["synthetic generic fixture"], "source_ref": "https://brand.example/generic", "confidence": "high"}
            for color in sorted(set(brand_profile.GENERIC_THEME["colors"].values()))
        ]
        generic.pop("theme_fingerprint", None)
        generic.pop("profile_fingerprint", None)
        with self.assertRaisesRegex(ValueError, "generic dashboard fallback"):
            dashboard.validate_brand_profile(generic)

    def test_brand_profile_rejects_unproven_tokens_and_stale_fingerprints(self) -> None:
        incomplete = self.brand_profile()
        incomplete["mappings"] = incomplete["mappings"][:-1]
        with self.assertRaisesRegex(ValueError, "must prove every theme token"):
            dashboard.validate_brand_profile(incomplete)

        stale = self.brand_profile()
        stale["profile_fingerprint"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "profile fingerprint is stale"):
            dashboard.validate_brand_profile(stale)

    def test_logo_only_primary_fails_but_evidenced_red_primary_remains_valid(self) -> None:
        logo_only = self.brand_profile()
        next(item for item in logo_only["observed_colors"] if item["value"] == "#006f8b")["usages"] = ["logo fill"]
        with self.assertRaisesRegex(ValueError, "global product role|logo-only"):
            dashboard.validate_brand_profile(logo_only)

        red_primary = self.brand_profile()
        next(item for item in red_primary["observed_colors"] if item["value"] == "#a63b2b")["usages"] = ["primary navigation accent"]
        next(item for item in red_primary["observed_colors"] if item["value"] == "#005f78")["usages"] = ["danger error"]
        red_primary["theme"]["colors"]["accent"] = "#a63b2b"
        red_primary["theme"]["colors"]["risk"] = "#005f78"
        validated = dashboard.validate_brand_profile(red_primary)
        self.assertEqual(validated["semantic_roles"]["primary"]["value"], "#a63b2b")
        self.assertNotEqual(validated["semantic_roles"]["primary"]["value"],
                            validated["semantic_roles"]["danger"]["value"])

    def test_brand_profile_changes_participate_in_dashboard_drift_check(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "index.html"
            changed_profile = root / "brand-profile.json"
            original = self.brand_profile()
            original.pop("theme_fingerprint", None)
            original.pop("profile_fingerprint", None)
            original.pop("asset_fingerprint", None)
            changed_profile.write_text(json.dumps(original), encoding="utf-8")
            subprocess.run([
                "python3", str(SCRIPT), "--data", str(EXAMPLE), "--brand-profile", str(changed_profile),
                "--output", str(output),
            ], check=True)
            original["theme"]["colors"]["accent"] = "#006b80"
            original["observed_colors"].append({
                "value": "#006b80", "usages": ["updated official accent"],
                "source_ref": "https://brand.example/assets/brand.css#--brand-primary-v2",
            })
            changed_profile.write_text(json.dumps(original), encoding="utf-8")
            checked = subprocess.run([
                "python3", str(SCRIPT), "--data", str(EXAMPLE), "--brand-profile", str(changed_profile),
                "--output", str(output), "--check",
            ], capture_output=True, text=True)
        self.assertEqual(checked.returncode, 1)
        self.assertIn("dashboard drift", checked.stdout)

    def test_required_dashboard_uses_accenture_fallback_when_brand_profile_is_missing(self) -> None:
        missing = self.data()
        missing["brand_required"] = True
        validated = dashboard.validate(missing)
        self.assertEqual(validated["brand_status"], "fallback")
        self.assertEqual(validated["brand_fallback"], "accenture")
        shell = (ROOT / "skills/build-living-dashboard/assets/dashboard-shell.html").read_text(encoding="utf-8")
        rendered = dashboard.render(validated, shell)
        self.assertIn('data-brand-id="accenture-fallback"', rendered)
        self.assertIn('data-brand-status="fallback"', rendered)

        optional = self.data()
        profile = self.brand_profile()
        profile["required"] = False
        profile.pop("profile_fingerprint", None)
        optional["brand_required"] = True
        optional["brand_profile"] = profile
        with self.assertRaisesRegex(ValueError, "supplied profile is optional"):
            dashboard.validate(optional)


if __name__ == "__main__":
    unittest.main()
