#!/usr/bin/env python3
"""Black-box scenarios for adaptive and natural-language initializer intake."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "initialize-project" / "scripts" / "initialize_project.py"


class NaturalLanguageBriefScenarios(unittest.TestCase):
    def run_brief(
        self,
        project: Path,
        brief: str,
        *arguments: str,
        dry_run: bool = True,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        command = [
            "python3", str(SCRIPT), "--root", str(project), "--name", "Brief project",
            "--runtime", "codex", "--no-git", "--brief", brief, *arguments,
        ]
        if dry_run:
            command.append("--dry-run")
        result = subprocess.run(command, capture_output=True, text=True)
        return result, json.loads(result.stdout)

    def test_interactive_mode_still_works_without_arguments(self) -> None:
        result = subprocess.run(["python3", str(SCRIPT)], check=True, capture_output=True, text=True)
        plan = json.loads(result.stdout)
        self.assertEqual(plan["mode"], "interactive")
        self.assertEqual(
            [entry["id"] for entry in plan["questions"]],
            ["project.scope", "project.goal", "project.runtime"],
        )
        self.assertTrue(plan["stopped_before_changes"])

    def test_positional_natural_language_brief_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run(
                [
                    "python3", str(SCRIPT), "--root", str(Path(temporary) / "project"),
                    "--runtime", "codex", "--dry-run", "legacy migration, SAS -> Java",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        plan = json.loads(result.stdout)
        self.assertEqual(plan["mode"], "brief-driven")
        self.assertEqual(plan["intake"]["known"]["source_technology"], "SAS")
        self.assertEqual(plan["intake"]["known"]["target_technology"], "Java")

    def test_a_fully_parameterized_legacy_request_uses_brand_fallback_and_asks_only_missing_language(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "legacy-sas"
            source.mkdir()
            (source / "main.sas").write_text("data target; set source; run;\n", encoding="utf-8")
            brief = (
                f"legacy migration, SAS -> Java, analysis + requirements dashboard + migration preparation, "
                f"source {source}, read-only"
            )
            result, plan = self.run_brief(Path(temporary) / "project", brief)
            self.assertEqual(result.returncode, 0, result.stderr)
            known = plan["intake"]["known"]
            self.assertEqual(known["scopes"], ["legacy-migration"])
            self.assertEqual((known["source_technology"], known["target_technology"]), ("SAS", "Java"))
            self.assertEqual(known["migration_intent"], "preparation")
            self.assertEqual(known["html_artifact"], "technical-dashboard")
            self.assertEqual(known["sources"][0]["access"], "read-only")
            self.assertTrue(plan["intake"]["inferred"]["evidence_traceability"])
            self.assertFalse(plan["intake"]["inferred"]["full_target_implementation"])
            question_ids = {entry["id"] for entry in plan["questions"]}
            self.assertEqual(question_ids, {"artifact.language"})
            self.assertNotIn("sources.location", question_ids)
            self.assertNotIn("migration.source_technology", question_ids)
            self.assertNotIn("migration.target_technology", question_ids)
            self.assertNotIn("project.deliverables", question_ids)

    def test_b_same_request_with_client_brand_does_not_ask_branding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "legacy-sas"
            source.mkdir()
            brief = (
                f"legacy migration, SAS -> Java, requirements dashboard + migration preparation, "
                f"source {source}, read-only, use client brand, audience both technical and management"
            )
            _, plan = self.run_brief(Path(temporary) / "project", brief)
            self.assertEqual(plan["intake"]["known"]["brand_source"], "client-brand")
            self.assertNotIn("dashboard.brand", {entry["id"] for entry in plan["questions"]})

    def test_c_brand_reference_url_is_captured_without_a_brand_question(self) -> None:
        brief = (
            "sales presentation about cloud modernization, use the branding from "
            "https://client.example, audience: CIO + enterprise architects\n"
            "desired outcome: approve a discovery workshop\nclient language: English"
        )
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            _, plan = self.run_brief(project, brief, dry_run=False)
            manifest = (project / ".agent-commons.yaml").read_text(encoding="utf-8")
        known = plan["intake"]["known"]
        self.assertEqual(known["brand_source"], "https://client.example")
        self.assertIn("https://client.example", known["references"])
        self.assertFalse(any(source["path"].endswith("client.example") for source in known["sources"]))
        self.assertNotIn("dashboard.brand", {entry["id"] for entry in plan["questions"]})
        self.assertIn('source: "https://client.example"', manifest)
        self.assertIn("scope: project-local", manifest)
        self.assertIn("copy_into_project: false", manifest)

    def test_d_partial_request_asks_only_material_missing_information(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            _, plan = self.run_brief(Path(temporary) / "project", "legacy migration, SAS -> Java")
        self.assertEqual(
            {entry["id"] for entry in plan["questions"]},
            {"sources.location", "migration.intent", "project.deliverables"},
        )

    def test_e_contradictory_source_permissions_stop_before_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "legacy"
            source.mkdir()
            brief = f"legacy SAS source {source} is read-only; update the source in-place"
            _, plan = self.run_brief(Path(temporary) / "project", brief)
            self.assertIn("source-permission-conflict", {entry["id"] for entry in plan["conflicts"]})
            self.assertTrue(plan["stopped_before_changes"])
            self.assertFalse((Path(temporary) / "project").exists())

    def test_f_multiple_read_only_sources_are_recorded_separately_and_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "sas"
            second = Path(temporary) / "copybooks"
            first.mkdir()
            second.mkdir()
            first_file = first / "main.sas"
            second_file = second / "record.cpy"
            first_file.write_text("data target; run;\n", encoding="utf-8")
            second_file.write_text("01 RECORD.\n", encoding="utf-8")
            before = (first_file.read_bytes(), second_file.read_bytes())
            brief = f"legacy analysis from {first} read-only and {second} read-only, extract requirements"
            _, plan = self.run_brief(Path(temporary) / "project", brief)
            sources = plan["intake"]["known"]["sources"]
            self.assertEqual(len(sources), 2)
            self.assertTrue(all(entry["access"] == "read-only" for entry in sources))
            self.assertEqual(before, (first_file.read_bytes(), second_file.read_bytes()))

    def test_g_development_brief_uses_the_same_extraction_path(self) -> None:
        brief = (
            "new development: React frontend, Spring Boot backend, PostgreSQL, Azure deployment, "
            "dashboard for technical status, use neutral premium branding"
        )
        with tempfile.TemporaryDirectory() as temporary:
            _, plan = self.run_brief(Path(temporary) / "project", brief)
        known = plan["intake"]["known"]
        self.assertEqual(known["scopes"], ["development"])
        self.assertEqual(known["html_artifact"], "technical-dashboard")
        self.assertEqual(known["brand_source"], "neutral-premium")
        self.assertIn("React", known["technologies"])
        self.assertIn("Spring Boot", known["technologies"])

    def test_g2_explicit_diagram_views_are_inferred_and_not_reasked(self) -> None:
        brief = (
            "development project. Build a service and document it. "
            "Need a component architecture, ER diagram, and login sequence diagram."
        )
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            result, plan = self.run_brief(project, brief, dry_run=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = (project / ".agent-commons.yaml").read_text(encoding="utf-8")
        self.assertEqual(
            plan["inferred"]["diagram_views"],
            ["component-architecture", "er", "sequence"],
        )
        self.assertEqual(plan["unresolved_questions"], [])
        self.assertIn('    - "architecture-documentation"', manifest)
        self.assertIn('    - "component-architecture-view"', manifest)
        self.assertIn('    - "er-data-model-view"', manifest)
        self.assertIn('    - "sequence-interaction-view"', manifest)
        self.assertIn('    - "create-component-architecture-diagram"', manifest)
        self.assertIn('    - "create-er-diagram"', manifest)
        self.assertIn('    - "create-sequence-diagram"', manifest)
        self.assertNotIn('    - "create-class-diagram"', manifest)

    def test_g3_unspecified_architecture_documentation_asks_one_view_question(self) -> None:
        brief = "development project with architecture documentation and implementation deliverables."
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            _, plan = self.run_brief(project, brief)
            self.assertFalse(project.exists())
        self.assertEqual([entry["id"] for entry in plan["questions"]], ["architecture.views"])
        self.assertIn("Migration roadmap", plan["questions"][0]["options"])

    def test_g4_architecture_assessment_routes_to_research_plus_landscape(self) -> None:
        brief = "architecture assessment: show all applications and integrations in a system landscape."
        with tempfile.TemporaryDirectory() as temporary:
            _, plan = self.run_brief(Path(temporary) / "project", brief)
        self.assertEqual(plan["intake"]["known"]["scopes"], ["research"])
        self.assertEqual(plan["intake"]["known"]["diagram_views"], ["system-landscape"])
        self.assertNotIn("architecture.views", {entry["id"] for entry in plan["questions"]})

    def test_h_presentation_brief_extracts_topic_brand_audience_and_outcome(self) -> None:
        brief = (
            "sales presentation about cloud modernization.\n"
            "Audience: CIO + enterprise architects\n"
            "Desired outcome: approve a discovery workshop\n"
            "Use the branding from https://client.example\nClient language: English"
        )
        with tempfile.TemporaryDirectory() as temporary:
            _, plan = self.run_brief(Path(temporary) / "project", brief)
        known = plan["intake"]["known"]
        self.assertEqual(known["scopes"], ["presentation"])
        self.assertEqual(known["presentation_topic"], "cloud modernization")
        self.assertIn("sales", known["presentation_purposes"])
        self.assertEqual(known["desired_outcome"], "approve a discovery workshop")
        self.assertEqual(plan["questions"], [])

    def test_i_hybrid_brief_composes_legacy_and_development(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "old-app"
            source.mkdir()
            (source / "Main.java").write_text("class Main {}\n", encoding="utf-8")
            brief = (
                f"hybrid: analyze legacy Java in {source} read-only, build replacement prototype here, "
                "and create an executive dashboard, neutral premium, audience management"
            )
            _, plan = self.run_brief(Path(temporary) / "project", brief)
        known = plan["intake"]["known"]
        self.assertEqual(known["scopes"], ["legacy-migration", "development"])
        self.assertIn("prototype", known["deliverables"])
        self.assertEqual(known["sources"][0]["access"], "read-only")
        self.assertNotIn("project.scope", {entry["id"] for entry in plan["questions"]})

    def test_j_supplied_facts_are_not_repeated_and_resolved_state_is_scaffolded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "legacy-sas"
            source.mkdir()
            source_file = source / "main.sas"
            source_file.write_text("data target; set source; run;\n", encoding="utf-8")
            before = source_file.read_bytes()
            project = Path(temporary) / "project"
            brief = (
                f"legacy migration, SAS -> Java; analyze source and extract requirements; prepare the migration; "
                f"source is {source} and read-only; create a technical dashboard for analysis and requirements; "
                "audience is technical and management; use Organization brand; client language English"
            )
            result, plan = self.run_brief(
                project,
                brief,
                "--capability-gap-strategy", "generic-only",
                dry_run=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(plan["questions"], [])
            self.assertFalse(plan["stopped_before_changes"])
            manifest = (project / ".agent-commons.yaml").read_text(encoding="utf-8")
            instructions = (project / "AGENTS.md").read_text(encoding="utf-8")
            dashboard = (project / "dashboard" / "index.html").read_text(encoding="utf-8")
            self.assertIn("intake_mode: brief-driven", manifest)
            self.assertIn('source_technology: "SAS"', manifest)
            self.assertIn('target_technology: "Java"', manifest)
            self.assertIn("intent: preparation", manifest)
            self.assertIn("access: read-only", manifest)
            self.assertIn('source: "organization"', manifest)
            self.assertIn("Source repositories/directories designated read-only may be analyzed but must never be modified.", instructions)
            self.assertIn('data-brand="organization"', dashboard)
            self.assertIn("No findings are asserted yet", dashboard)
            self.assertNotIn('"value":"50%"', dashboard)
            self.assertNotIn(">50%<", dashboard)
            self.assertIn('data-canonical-section="overview"', dashboard)
            self.assertIn('data-canonical-section="requirements"', dashboard)
            self.assertIn('data-canonical-section="specifications"', dashboard)
            self.assertIn('data-dashboard-hook="canonical-navigation"', dashboard)
            self.assertEqual(source_file.read_bytes(), before)

    def test_k_bilingual_austrian_client_delivery_is_inferred_without_reasking(self) -> None:
        brief = (
            "New development with an English working dashboard for management. Use neutral premium branding. "
            "Client delivery: Austrian German + English switch."
        )
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            result, plan = self.run_brief(project, brief, dry_run=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = (project / ".agent-commons.yaml").read_text(encoding="utf-8")
        self.assertNotIn("artifact.language", {entry["id"] for entry in plan["questions"]})
        self.assertEqual(plan["inferred"]["working_language"], "en")
        self.assertEqual(plan["inferred"]["dashboard_languages"], ["de-AT", "en"])
        self.assertEqual(plan["inferred"]["dashboard_default_language"], "de-AT")
        self.assertTrue(plan["inferred"]["dashboard_language_switch"])
        self.assertIn('    - "bilingual-client-delivery"', manifest)
        self.assertIn('  working_language: "en"', manifest)
        self.assertIn('dashboard:\n  enabled: true', manifest)
        self.assertIn('  languages:\n    - "de-AT"\n    - "en"', manifest)
        self.assertIn('  default_language: "de-AT"', manifest)
        self.assertIn('  language_switch: true', manifest)
        self.assertNotIn('  client_language:', manifest)

    def test_l_unresolved_html_language_gets_one_concise_question(self) -> None:
        brief = "Create a management dashboard for executives using neutral premium branding."
        with tempfile.TemporaryDirectory() as temporary:
            _, plan = self.run_brief(Path(temporary) / "project", brief)
        language_questions = [entry for entry in plan["questions"] if entry["id"] == "artifact.language"]
        self.assertEqual(len(language_questions), 1)
        self.assertEqual(
            language_questions[0]["options"],
            ["English", "German (Austria)", "German + English switch", "Other"],
        )

    def test_prepare_migration_is_not_treated_as_full_implementation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            _, preparation = self.run_brief(
                Path(temporary) / "prepare",
                "legacy migration SAS -> Java, prepare the migration, migration plan",
            )
            _, implementation = self.run_brief(
                Path(temporary) / "implement",
                "legacy migration SAS -> Java, implement the migration",
            )
        self.assertEqual(preparation["intake"]["known"]["migration_intent"], "preparation")
        self.assertNotIn("development", preparation["intake"]["known"]["scopes"])
        self.assertEqual(implementation["intake"]["known"]["migration_intent"], "implementation")
        self.assertIn("development", implementation["intake"]["known"]["scopes"])

    def test_conversational_source_target_notation_is_understood(self) -> None:
        cases = [
            ("migrate COBOL to C#", "COBOL", "C#"),
            ("modernize AngularJS to React", "AngularJS", "React"),
            ("migrate legacy Spring to Spring Boot 4", "Spring", "Spring Boot 4"),
            ("analyse the old Java app and prepare a Spring Boot replacement", "Java", "Spring Boot"),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            for index, (brief, source, target) in enumerate(cases):
                with self.subTest(brief=brief):
                    _, plan = self.run_brief(Path(temporary) / f"project-{index}", brief)
                    known = plan["intake"]["known"]
                    self.assertEqual(known["source_technology"], source)
                    self.assertEqual(known["target_technology"], target)
                    if source == "Java":
                        self.assertEqual(known["migration_intent"], "preparation")

    def test_source_inspection_resolves_a_discoverable_source_technology(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            source.mkdir()
            (source / "program.sas").write_text("data target; run;\n", encoding="utf-8")
            _, plan = self.run_brief(
                Path(temporary) / "project",
                f"legacy analysis from {source}, read-only, extract requirements",
            )
        self.assertEqual(plan["intake"]["discovered"]["source_technology"], "SAS")
        self.assertNotIn("migration.source_technology", {entry["id"] for entry in plan["questions"]})

    def test_exact_parallel_brand_benchmark_preserves_facts_and_builds_safe_shell(self) -> None:
        brief = (
            "Initialize project. Analyze legacy code under read-only client_input. Extract requirements. "
            "Create specifications. Eventually modernize to Java 21 / Spring Boot 4.x. Use client branding: "
            "https://federal-office.gv.at/corporate-design"
        )
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            source = workspace / "client_input"
            source.mkdir()
            source_file = source / "sample.cbl"
            source_file.write_text("IDENTIFICATION DIVISION.\n", encoding="utf-8")
            before = source_file.read_bytes()
            project = workspace / "project"
            result = subprocess.run(
                [
                    "python3", str(SCRIPT), "--root", str(project), "--runtime", "codex",
                    "--no-git", "--brief", brief,
                ],
                cwd=workspace,
                capture_output=True,
                text=True,
            )
            plan = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(plan["questions"], [])
            self.assertFalse(plan["stopped_before_changes"])
            self.assertFalse(plan["choice_required"])
            self.assertTrue(plan["safe_initialization_continues"])
            self.assertFalse(plan["capability_dependent_work_blocked"])
            self.assertTrue(plan["automatic_external_search"])
            self.assertEqual(plan["external_discovery"]["status"], "running")
            known = plan["intake"]["known"]
            self.assertEqual(known["target_technology"], "Java 21 / Spring Boot 4.x")
            self.assertEqual(known["brand_source"], "https://federal-office.gv.at/corporate-design")
            self.assertEqual(known["sources"][0]["access"], "read-only")
            self.assertIn("openspec-specifications", known["deliverables"])
            stages = plan["execution_plan"]["stages"]
            self.assertEqual(
                set(stages[1]["task_ids"]),
                {"brand-resolution", "commons-resolution", "environment-inspection", "source-inspection"},
            )
            self.assertTrue((project / "analysis" / "source-inventory.json").is_file())
            dashboard = (project / "dashboard" / "index.html").read_text(encoding="utf-8")
            dashboard_data = json.loads((project / "dashboard" / "data.json").read_text(encoding="utf-8"))
            self.assertIn('data-brand-id="accenture-fallback"', dashboard)
            self.assertIn('data-brand-status="fallback"', dashboard)
            self.assertEqual(dashboard_data["brand_requested_source"], "https://federal-office.gv.at/corporate-design")
            self.assertEqual(dashboard_data["brand_fallback"], "accenture")
            self.assertFalse((project / "dashboard" / "BRANDING-BLOCKED.md").exists())
            self.assertEqual(before, source_file.read_bytes())

    def test_analysis_only_requirements_dashboard_does_not_enable_specs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "legacy"
            source.mkdir()
            (source / "main.cbl").write_text("IDENTIFICATION DIVISION.\n", encoding="utf-8")
            project = Path(temporary) / "project"
            _, plan = self.run_brief(
                project,
                f"Analyze only legacy COBOL source {source}, extract requirements and create requirements dashboard using neutral premium, audience management, client language English",
                dry_run=False,
            )
            manifest = (project / ".agent-commons.yaml").read_text(encoding="utf-8")
            dashboard = (project / "dashboard" / "index.html").read_text(encoding="utf-8")
        self.assertEqual(plan["intake"]["inferred"]["specifications"], "none")
        self.assertIn("  method: none", manifest)
        self.assertIn("  show_specifications: false", manifest)
        self.assertIn('data-canonical-section="requirements"', dashboard)
        self.assertIn('data-canonical-section="specifications"', dashboard)
        self.assertIn('data-section-applicability="not-applicable"', dashboard)
        self.assertNotIn('data-canonical-section="roadmap"', dashboard)
        self.assertNotIn('data-canonical-section="validation"', dashboard)
        self.assertIn("Analysis in progress", dashboard)

    def test_prepare_implementation_enables_specs_but_defers_tdd(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            _, plan = self.run_brief(
                project,
                "Legacy migration COBOL -> Java. Analyze source, extract requirements, prepare implementation, and create technical dashboard. Source ./missing, use neutral premium, audience both, client language English",
                "--capability-gap-strategy", "generic-only",
                dry_run=False,
            )
            manifest = (project / ".agent-commons.yaml").read_text(encoding="utf-8")
        self.assertEqual(plan["intake"]["known"]["migration_intent"], "preparation")
        self.assertEqual(plan["intake"]["inferred"]["specifications"], "openspec")
        self.assertEqual(plan["intake"]["inferred"]["tdd"], "planned")
        self.assertNotIn("implementation", plan["intake"]["known"]["deliverables"])
        self.assertIn("  method: openspec", manifest)
        self.assertIn("  method: test-driven-development", manifest)
        self.assertIn("  phase: planned", manifest)
        self.assertIn('    - "migration-openspec-preparation"', manifest)

    def test_spring_boot_development_defaults_to_openspec_and_tdd(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            _, plan = self.run_brief(project, "Spring Boot development", dry_run=False)
            manifest = (project / ".agent-commons.yaml").read_text(encoding="utf-8")
        self.assertIn("development", plan["intake"]["known"]["scopes"])
        self.assertIn('    - "specify-openspec-change"', manifest)
        self.assertIn('    - "test-driven-development"', manifest)
        self.assertIn("  phase: active", manifest)

    def test_full_stack_development_defaults_without_methodology_questions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            _, plan = self.run_brief(
                project,
                "New development: React frontend, Spring Boot backend, PostgreSQL",
                dry_run=False,
            )
            manifest = (project / ".agent-commons.yaml").read_text(encoding="utf-8")
        self.assertEqual(plan["methodology"]["specification"], "openspec")
        self.assertEqual(plan["methodology"]["implementation"], "test-driven-development")
        self.assertFalse(any("OpenSpec" in q["question"] or "TDD" in q["question"] for q in plan["questions"]))
        self.assertIn('    - "specify-openspec-change"', manifest)
        self.assertIn('    - "test-driven-development"', manifest)

    def test_explicit_no_openspec_is_respected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            _, plan = self.run_brief(project, "Quick prototype development, no OpenSpec", dry_run=False)
            manifest = (project / ".agent-commons.yaml").read_text(encoding="utf-8")
            commons = manifest.split("commons:", 1)[1].split("capability_state:", 1)[0]
        self.assertEqual(plan["methodology"]["specification"], "none")
        self.assertEqual(plan["methodology"]["specification_state"], "explicit-opt-out")
        self.assertNotIn('    - "specify-openspec-change"', commons)
        self.assertIn('    - "test-driven-development"', commons)

    def test_explicit_no_tdd_is_respected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            _, plan = self.run_brief(
                project, "New development experiment, use normal implementation, no TDD", dry_run=False,
            )
            manifest = (project / ".agent-commons.yaml").read_text(encoding="utf-8")
            commons = manifest.split("commons:", 1)[1].split("capability_state:", 1)[0]
        self.assertEqual(plan["methodology"]["implementation"], "normal")
        self.assertEqual(plan["methodology"]["implementation_state"], "explicit-opt-out")
        self.assertIn('    - "specify-openspec-change"', commons)
        self.assertNotIn('    - "test-driven-development"', commons)

    def test_legacy_implementation_activates_openspec_and_tdd(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            _, plan = self.run_brief(
                Path(temporary) / "project",
                "Legacy migration COBOL -> Java, implement the migration, source ./legacy",
                "--capability-gap-strategy", "generic-only",
            )
        self.assertEqual(plan["methodology"]["specification"], "openspec")
        self.assertEqual(plan["methodology"]["implementation"], "test-driven-development")
        self.assertEqual(plan["methodology"]["phase"], "active")
        self.assertIn("development", plan["intake"]["known"]["scopes"])

    def test_research_and_presentation_do_not_select_delivery_methodology(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            for index, brief in enumerate((
                "Research cloud modernization, topic: cloud modernization, research goal: inform strategy",
                "Technical presentation about architecture, audience: engineering, purpose: technical, desired outcome: understand architecture",
            )):
                with self.subTest(brief=brief):
                    _, plan = self.run_brief(Path(temporary) / f"project-{index}", brief)
                    self.assertEqual(plan["methodology"]["specification"], "none")
                    self.assertEqual(plan["methodology"]["implementation"], "none")

    def test_existing_openspec_project_is_reused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            (project / "openspec").mkdir(parents=True)
            (project / "openspec/config.yaml").write_text("schema: spec-driven\n", encoding="utf-8")
            before = (project / "openspec/config.yaml").read_text(encoding="utf-8")
            _, plan = self.run_brief(project, "New development: React application", dry_run=False)
            manifest = (project / ".agent-commons.yaml").read_text(encoding="utf-8")
            self.assertEqual((project / "openspec/config.yaml").read_text(encoding="utf-8"), before)
        self.assertEqual(plan["methodology"]["specification_state"], "reuse")
        self.assertIn("openspec/config.yaml", plan["methodology"]["evidence"])
        self.assertIn("  state: reuse", manifest)

    def test_existing_alternative_specification_method_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            (project / ".specify").mkdir(parents=True)
            _, plan = self.run_brief(project, "New development: React application", dry_run=False)
            manifest = (project / ".agent-commons.yaml").read_text(encoding="utf-8")
            commons = manifest.split("commons:", 1)[1].split("capability_state:", 1)[0]
        self.assertEqual(plan["methodology"]["specification"], "spec-kit")
        self.assertEqual(plan["methodology"]["specification_state"], "preserve")
        self.assertNotIn('    - "specify-openspec-change"', commons)
        self.assertIn("  method: spec-kit", manifest)

    def test_explicit_openspec_conflicts_with_existing_alternative(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            (project / ".specify").mkdir(parents=True)
            _, plan = self.run_brief(project, "New development, use OpenSpec")
        self.assertTrue(plan["stopped_before_changes"])
        self.assertIn("specification-method-conflict", {item["id"] for item in plan["conflicts"]})

    def test_existing_manifest_methodology_is_detected_without_cross_section_guessing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            (project / ".agent-commons.yaml").write_text(
                "specifications:\n  method: contract-first\nimplementation:\n  method: normal\n",
                encoding="utf-8",
            )
            _, plan = self.run_brief(project, "New development: API service")
        self.assertEqual(plan["methodology"]["specification"], "contract-first")
        self.assertEqual(plan["methodology"]["implementation"], "normal")
        self.assertEqual(plan["methodology"]["specification_state"], "preserve")
        self.assertEqual(plan["methodology"]["implementation_state"], "preserve")


if __name__ == "__main__":
    unittest.main()
