#!/usr/bin/env python3
"""Black-box initializer evaluations using temporary directories only."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "initialize-project" / "scripts" / "initialize_project.py"
PROJECT_RUNTIMES = ROOT / "tools" / "project_runtimes.py"
GAP_RESOLVER = ROOT / "tools" / "resolve_capability_gaps.py"
SEARCH_SKILL = ROOT / "skills" / "search-external-capabilities" / "SKILL.md"


class InitializerScenarios(unittest.TestCase):
    def initialize(self, *arguments: str) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        target = Path(temporary.name) / "project"
        subprocess.run(
            ["python3", str(SCRIPT), "--root", str(target), "--name", "Synthetic project",
             "--goal", "Produce the agreed synthetic deliverable", "--done", "Acceptance checks pass",
             "--no-git", "--runtime", "codex", *arguments],
            check=True,
            capture_output=True,
            text=True,
        )
        return target

    def manifest(self, target: Path) -> str:
        return (target / ".agent-commons.yaml").read_text(encoding="utf-8")

    def run_initializer(self, target: Path, *arguments: str) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        result = subprocess.run(
            ["python3", str(SCRIPT), "--root", str(target), "--name", "Synthetic migration",
             "--goal", "Extract requirements and prepare migration", "--done", "Parity checks pass",
             "--scope", "legacy-migration,development", "--scale", "standard", "--runtime", "codex",
             "--overlay", "evidence-traceability", "--source-technology", "SAS",
             "--target-technology", "Java", "--validation", "Migration parity validation",
             "--no-git", *arguments],
            capture_output=True,
            text=True,
        )
        return result, json.loads(result.stdout)

    def test_a_legacy_modernization(self) -> None:
        target = self.initialize("--scope", "legacy", "--scale", "standard",
                                 "--html-artifact", "technical-dashboard", "--read-only-path", "legacy-source/",
                                 "--overlay", "evidence-traceability")
        manifest = self.manifest(target)
        self.assertIn("analyze-legacy-system", manifest)
        self.assertIn("derive-modernization-requirements", manifest)
        self.assertIn("legacy-migration", manifest)
        self.assertIn("evidence-traceability", manifest)
        self.assertIn('"legacy-source/"', manifest)
        self.assertIn("  template: canonical", manifest)
        self.assertIn("  template_id: agent-commons-living-dashboard", manifest)
        self.assertIn("  visual_contract: agent-commons-living-dashboard-v3", manifest)
        self.assertIn("  fallback_policy: block-if-canonical-resources-unavailable", manifest)
        self.assertTrue((target / "dashboard" / "index.html").is_file())
        dashboard = (target / "dashboard" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-dashboard-design-id="agent-commons-living-dashboard-v3"', dashboard)
        self.assertIn('data-canonical-section="overview"', dashboard)
        self.assertIn('data-canonical-section="inventory"', dashboard)
        self.assertIn('data-canonical-section="dependencies"', dashboard)
        self.assertIn('data-canonical-section="stakeholder-questions"', dashboard)
        self.assertIn('data-canonical-section="database"', dashboard)
        self.assertIn('data-canonical-section="test-quality"', dashboard)
        self.assertNotIn('data-canonical-section="roadmap"', dashboard)
        dashboard_data = json.loads((target / "dashboard" / "data.json").read_text(encoding="utf-8"))
        domain_states = {
            item["id"]: item["status"]
            for item in dashboard_data["dashboard_structure"]["information_domains"]
        }
        self.assertEqual(domain_states["complexity"], "NOT_YET_ANALYZED")
        self.assertEqual(domain_states["estimation"], "NOT_YET_ANALYZED")
        self.assertEqual(domain_states["open-questions"], "NOT_YET_ANALYZED")
        self.assertEqual(set(domain_states), {
            item["id"] for item in json.loads(
                (ROOT / "skills/build-living-dashboard/assets/dashboard-structure.json").read_text(encoding="utf-8")
            )["information_domains"]
        })

    def test_b_greenfield_development(self) -> None:
        target = self.initialize("--scope", "development", "--scale", "standard",
                                 "--html-artifact", "project-dashboard", "--technology", "Python",
                                 "--deliverable", "Working web application")
        manifest = self.manifest(target)
        self.assertIn("implement-ready-slice", manifest)
        self.assertIn("living-dashboard", manifest)
        self.assertIn('"Python"', manifest)
        self.assertFalse((target / "docs").exists())

    def test_successful_initialization_returns_and_persists_exact_next_action(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            legacy = Path(temporary) / "legacy"
            result = subprocess.run([
                "python3", str(SCRIPT), "--root", str(legacy), "--name", "Legacy",
                "--scope", "legacy-migration", "--runtime", "codex", "--no-git",
                "--goal", "Analyze legacy behavior", "--deliverable", "requirements-extraction",
            ], check=True, capture_output=True, text=True)
            plan = json.loads(result.stdout)
            manifest = self.manifest(legacy)
            self.assertEqual(plan["result"], "initialized")
            self.assertEqual(plan["message"], "Project initialized.")
            self.assertEqual(plan["next_action"]["command"], "$analyze-legacy-system")
            self.assertIn("lifecycle:\n  schema_version: 1", manifest)
            self.assertIn("capability: analyze-legacy-system", manifest)

            development = Path(temporary) / "development"
            result = subprocess.run([
                "python3", str(SCRIPT), "--root", str(development), "--name", "Development",
                "--scope", "development", "--runtime", "codex", "--no-git",
                "--goal", "Build a service",
            ], check=True, capture_output=True, text=True)
            plan = json.loads(result.stdout)
            self.assertEqual(plan["next_action"]["command"], "$specify-openspec-change")
            self.assertIn("Next action: `$specify-openspec-change`", (development / "README.md").read_text(encoding="utf-8"))

    def test_c_client_presentation(self) -> None:
        target = self.initialize("--scope", "presentation", "--scale", "standard",
                                 "--html-artifact", "executive-presentation", "--brand-source", "supplied-assets")
        manifest = self.manifest(target)
        self.assertIn("create-branded-html-artifact", manifest)
        self.assertIn("branded-html", manifest)
        self.assertIn('source: "supplied-assets"', manifest)
        presentation = (target / "presentation" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-brand-id="accenture-fallback"', presentation)
        self.assertIn('data-brand-status="fallback"', presentation)
        self.assertFalse((target / "presentation" / "BRANDING-BLOCKED.md").exists())

    def test_research_only_creates_evidence_base_without_presentation(self) -> None:
        target = self.initialize(
            "--scope", "research", "--scale", "standard",
            "--research-topic", "European banking modernization",
            "--research-goal", "Support a market-entry decision",
        )
        manifest = self.manifest(target)
        self.assertIn('    - "deep-research"', manifest)
        self.assertIn('    - "research"', manifest)
        self.assertTrue((target / "research" / "research-plan.md").is_file())
        self.assertTrue((target / "research" / "synthesis.md").is_file())
        self.assertFalse((target / "presentation").exists())

    def test_presentation_from_existing_research_does_not_repeat_research(self) -> None:
        target = self.initialize(
            "--scope", "presentation", "--scale", "standard",
            "--presentation-topic", "Modernization options",
            "--presentation-purpose", "technical",
            "--audience", "enterprise architects",
            "--desired-outcome", "Select an architecture workshop",
            "--source-material", "existing-research/findings.md",
            "--html-artifact", "executive-presentation",
        )
        manifest = self.manifest(target)
        self.assertNotIn('    - "deep-research"', manifest)
        self.assertIn('  - "existing-research/findings.md"', manifest)
        self.assertFalse((target / "research").exists())
        self.assertTrue((target / "presentation" / "index.html").is_file())

    def test_natural_language_research_sales_presentation_extracts_supplied_values(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            brief = """research + sales presentation about AI modernization
Audience: CIO + enterprise architects
Desired outcome: approve a workshop
Brand: client
Client language: English
References:
- /examples/timeline.png for timeline structure, not colors
- /examples/cluster.png for cluster design
- /examples/good-deck.pdf for storytelling and density"""
            result = subprocess.run(
                ["python3", str(SCRIPT), "--root", str(target), "--name", "Research sales",
                 "--runtime", "codex", "--no-git", "--brief", brief],
                check=True,
                capture_output=True,
                text=True,
            )
            plan = json.loads(result.stdout)
            manifest = self.manifest(target)
            self.assertEqual(plan["unresolved_questions"], [])
            self.assertEqual(plan["inferred"]["scopes"], ["research", "presentation"])
            self.assertEqual(plan["inferred"]["audience"], ["CIO", "enterprise architects"])
            self.assertIn('    - "sales-storytelling"', manifest)
            self.assertIn('    - "deep-research"', manifest)
            self.assertIn('source: "/examples/timeline.png"', manifest)
            self.assertIn('      - "timeline"', manifest)
            self.assertIn('      - "structure"', manifest)
            self.assertIn('      - "colors"', manifest)
            self.assertIn('source: "client-brand"', manifest)
            self.assertTrue((target / "references" / "README.md").is_file())
            self.assertTrue((target / "research" / "synthesis.md").is_file())
            presentation = (target / "presentation" / "index.html").read_text(encoding="utf-8")
            self.assertIn('data-brand-id="accenture-fallback"', presentation)
            self.assertIn('data-brand-status="fallback"', presentation)
            self.assertFalse((target / "presentation" / "BRANDING-BLOCKED.md").exists())

    def test_bilingual_client_delivery_flags_select_overlay_and_manifest_configuration(self) -> None:
        target = self.initialize(
            "--scope", "presentation", "--scale", "standard",
            "--presentation-topic", "Modernization decision",
            "--presentation-purpose", "executive",
            "--audience", "client leadership",
            "--desired-outcome", "Approve the next phase",
            "--html-artifact", "executive-presentation",
            "--working-language", "en",
            "--client-language", "de-AT",
            "--bilingual",
        )
        manifest = self.manifest(target)
        self.assertIn('    - "bilingual-client-delivery"', manifest)
        self.assertIn('    - "localize-client-artifact"', manifest)
        self.assertIn('  working_language: "en"', manifest)
        self.assertIn('presentation:\n  enabled: true', manifest)
        self.assertIn('  languages:\n    - "de-AT"\n    - "en"', manifest)
        self.assertIn('  default_language: "de-AT"', manifest)
        self.assertIn('  bilingual: true', manifest)
        self.assertNotIn('  client_language:', manifest)
        self.assertEqual(manifest.count('    - "validate-visual-artifact"\n'), 1)

    def test_presentation_without_references_proceeds_and_offers_optional_question(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            result = subprocess.run(
                ["python3", str(SCRIPT), "--root", str(target), "--name", "No references",
                 "--scope", "presentation", "--presentation-topic", "Architecture",
                 "--presentation-purpose", "informational", "--audience", "engineering leadership",
                 "--desired-outcome", "Understand the architecture", "--html-artifact", "executive-presentation",
                 "--brand-source", "neutral-premium", "--runtime", "codex", "--no-git"],
                check=True,
                capture_output=True,
                text=True,
            )
            plan = json.loads(result.stdout)
            self.assertEqual(len(plan["optional_questions"]), 1)
            self.assertFalse((target / "references").exists())

    def test_presentation_only_combination_uses_accenture_fallback_for_unresolved_client_brand(self) -> None:
        target = self.initialize(
            "--scope", "presentation", "--scale", "standard",
            "--html-artifact", "combination", "--brand-source", "supplied-assets",
        )
        presentation = (target / "presentation" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-brand-id="accenture-fallback"', presentation)
        self.assertIn('data-brand-status="fallback"', presentation)
        self.assertFalse((target / "presentation" / "BRANDING-BLOCKED.md").exists())
        self.assertFalse((target / "dashboard").exists())

    def test_d_tiny_project_stays_tiny(self) -> None:
        target = self.initialize("--scope", "development", "--scale", "tiny", "--html-artifact", "none")
        manifest = self.manifest(target)
        self.assertIn("skills: []", manifest)
        self.assertIn("agents: []", manifest)
        self.assertIn("archetypes:", manifest)
        self.assertIn("development", manifest)
        self.assertFalse((target / "docs").exists())
        self.assertFalse((target / ".agents").exists())
        self.assertFalse((target / ".codex").exists())
        self.assertFalse((target / "dashboard").exists())
        self.assertIn("mode: skipped", manifest)
        self.assertIn("project_memory:\n  enabled: false", manifest)
        self.assertFalse((target / ".agent-commons").exists())
        self.assertNotIn("Optional external capability research", (target / "README.md").read_text(encoding="utf-8"))

    def test_standard_project_enables_lazy_hierarchical_memory_automatically(self) -> None:
        for scope in ("legacy", "development", "research", "presentation"):
            with self.subTest(scope=scope):
                target = self.initialize("--scope", scope, "--scale", "standard")
                manifest = self.manifest(target)
                self.assertIn('    - "durable-state"', manifest)
                self.assertIn('    - "maintain-project-memory"', manifest)
                self.assertIn("project_memory:\n  enabled: true", manifest)
                self.assertIn('  root: ".agent-commons/memory"', manifest)
                self.assertIn("  lazy: true", manifest)
                self.assertIn("  hierarchy: L0-L1-L2-EVIDENCE", manifest)

    def test_fully_covered_standard_project_does_not_prompt_for_external_research(self) -> None:
        target = self.initialize("--scope", "legacy", "--scale", "standard")
        manifest = self.manifest(target)
        self.assertIn("mode: skipped", manifest)
        self.assertIn("automatic_search: false", manifest)
        readme = (target / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("Optional external capability research", readme)
        self.assertIn("requires_user_choice: false", manifest)

    def test_standard_project_can_skip_external_research(self) -> None:
        target = self.initialize(
            "--scope", "development", "--scale", "standard", "--external-research", "skip",
        )
        self.assertIn("mode: skipped", self.manifest(target))
        self.assertNotIn("Optional external capability research", (target / "README.md").read_text(encoding="utf-8"))

    def test_user_can_explicitly_request_non_gap_external_research(self) -> None:
        target = self.initialize(
            "--scope", "development", "--scale", "standard", "--external-research", "suggest",
            "--external-discovery-snapshot", str(ROOT / "evals/fixtures/external/github-snapshot.json"),
        )
        self.assertIn("mode: running-concurrently", self.manifest(target))
        self.assertIn("automatic_search: true", self.manifest(target))
        self.assertIn("External capability discovery", (target / "README.md").read_text(encoding="utf-8"))
        state_path = target / ".agent-commons" / "external-discovery.json"
        for _ in range(100):
            if json.loads(state_path.read_text(encoding="utf-8"))["status"] != "running":
                break
            time.sleep(0.02)

    def test_e_hybrid_composes_without_copies(self) -> None:
        target = self.initialize("--scope", "legacy,development,presentation", "--scale", "standard",
                                 "--html-artifact", "combination")
        manifest = self.manifest(target)
        for capability in ("inventory-codebase", "analyze-legacy-system", "implement-ready-slice",
                           "create-branded-html-artifact", "build-living-dashboard"):
            self.assertIn(capability, manifest)
        self.assertEqual(manifest.count('    - "validate-visual-artifact"\n'), 1)
        self.assertFalse((target / ".agents").exists())
        self.assertFalse((target / ".codex").exists())

    def test_generated_instructions_are_project_specific(self) -> None:
        target = self.initialize(
            "--scope", "development", "--scale", "standard", "--context", "product",
            "--deliverable", "Synthetic CLI", "--technology", "Python 3",
            "--reference", "docs/spec.md", "--constraint", "Keep the CLI offline",
            "--validation", "python3 -m unittest",
        )
        instructions = (target / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Synthetic CLI", instructions)
        self.assertIn("Python 3", instructions)
        self.assertIn("docs/spec.md", instructions)
        self.assertIn("Keep the CLI offline", instructions)
        self.assertIn("python3 -m unittest", instructions)
        self.assertIn("## Git commits", instructions)
        self.assertIn("Do not use Conventional Commit type prefixes", instructions)
        self.assertIn("prefix the message with `[TICKET-ID]`", instructions)
        self.assertIn("Do not add `Co-authored-by`", instructions)
        manifest = self.manifest(target)
        self.assertIn("library_revision:", manifest)
        self.assertIn("context: product", manifest)

    def test_project_runtime_status_reports_canonical_skill_references(self) -> None:
        target = self.initialize("--scope", "legacy", "--scale", "standard")
        result = subprocess.run(
            ["python3", str(PROJECT_RUNTIMES), "status", "--root", str(target)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("capability_reference_mode=canonical-stable-id", result.stdout)
        self.assertIn("selected_skills=", result.stdout)
        self.assertIn("analyze-legacy-system", result.stdout)
        self.assertIn("automatic_execution=false", result.stdout)

    def test_multi_runtime_project_uses_one_shared_context_and_thin_claude_adapter(self) -> None:
        target = self.initialize(
            "--scope", "development", "--scale", "standard", "--runtime", "claude-code",
        )
        manifest = self.manifest(target)
        self.assertIn("    - codex", manifest)
        self.assertIn("    - claude-code", manifest)
        self.assertTrue((target / "AGENTS.md").is_file())
        claude = (target / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertTrue(claude.startswith("@AGENTS.md\n"))
        self.assertNotIn("Produce the agreed synthetic deliverable", claude)
        self.assertFalse((target / ".codex").exists())
        self.assertFalse((target / ".claude").exists())

    def test_all_runtimes_share_the_generated_git_policy(self) -> None:
        target = self.initialize(
            "--scope", "development", "--scale", "standard",
            "--runtime", "claude-code", "--runtime", "cline", "--runtime", "opencode",
        )
        manifest = self.manifest(target)
        for runtime in ("codex", "claude-code", "cline", "opencode"):
            self.assertIn(f"    - {runtime}", manifest)
        instructions = (target / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Do not use Conventional Commit type prefixes", instructions)
        self.assertIn("Do not add `Co-authored-by`", instructions)
        self.assertTrue((target / "CLAUDE.md").read_text(encoding="utf-8").startswith("@AGENTS.md\n"))

    def test_runtime_detection_uses_existing_native_markers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            (target / ".claude").mkdir(parents=True)
            result = subprocess.run(
                ["python3", str(SCRIPT), "--root", str(target), "--name", "Detected", "--scope",
                 "development", "--scale", "tiny", "--no-git"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn('"runtimes": [\n    "claude-code"', result.stdout)
            self.assertIn("    - claude-code", self.manifest(target))
            self.assertTrue((target / "CLAUDE.md").is_file())

    def test_removing_one_project_adapter_preserves_canonical_context(self) -> None:
        target = self.initialize(
            "--scope", "development", "--scale", "standard", "--runtime", "claude-code",
        )
        before_agents = (target / "AGENTS.md").read_text(encoding="utf-8")
        subprocess.run(
            ["python3", str(PROJECT_RUNTIMES), "remove", "--root", str(target), "--runtime", "claude-code"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertFalse((target / "CLAUDE.md").exists())
        self.assertEqual((target / "AGENTS.md").read_text(encoding="utf-8"), before_agents)
        manifest = self.manifest(target)
        self.assertIn("    - codex", manifest)
        self.assertNotIn("    - claude-code", manifest)
        subprocess.run(
            ["python3", str(PROJECT_RUNTIMES), "verify", "--root", str(target)],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_empty_project_requires_explicit_runtime_in_noninteractive_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            result = subprocess.run(
                ["python3", str(SCRIPT), "--root", str(target), "--name", "Unknown", "--scope",
                 "development", "--scale", "tiny", "--no-git"],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("runtime could not be detected", result.stderr)

    def test_presentation_can_decline_html(self) -> None:
        target = self.initialize("--scope", "presentation", "--scale", "standard", "--html-artifact", "none")
        manifest = self.manifest(target)
        self.assertNotIn("create-branded-html-artifact", manifest)
        self.assertNotIn("validate-visual-artifact", manifest)
        self.assertFalse((target / "presentation").exists())

    def test_existing_files_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            target.mkdir()
            readme = target / "README.md"
            readme.write_text("user-owned\n", encoding="utf-8")
            subprocess.run(
                ["python3", str(SCRIPT), "--root", str(target), "--name", "Existing", "--scope",
                 "development", "--scale", "tiny", "--no-git", "--runtime", "codex"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(readme.read_text(encoding="utf-8"), "user-owned\n")

    def test_project_local_capability_stays_in_selected_runtime_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            skill = target / ".claude" / "skills" / "project-only" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            content = "# Project-only skill\n\nThis capability must remain local.\n"
            skill.write_text(content, encoding="utf-8")
            subprocess.run(
                ["python3", str(SCRIPT), "--root", str(target), "--name", "Local capability",
                 "--scope", "development", "--scale", "tiny", "--no-git", "--runtime", "claude-code"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(skill.read_text(encoding="utf-8"), content)
            self.assertNotIn("project-only", self.manifest(target))
            self.assertFalse((target / ".agents" / "skills" / "project-only").exists())

    def test_unsafe_home_root_is_rejected(self) -> None:
        result = subprocess.run(
            ["python3", str(SCRIPT), "--root", str(Path.home()), "--name", "Unsafe", "--scope",
             "development", "--scale", "tiny", "--dry-run", "--no-git", "--runtime", "codex"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing to initialize", result.stderr)

    def test_k_missing_technology_capability_preserves_safe_setup(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            result, plan = self.run_initializer(
                target, "--external-discovery-snapshot", str(ROOT / "evals/fixtures/external/github-snapshot.json"),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(plan["choice_required"])
            self.assertEqual(plan["choices"], [])
            self.assertTrue(plan["automatic_external_search"])
            gaps = {entry["id"]: entry["status"] for entry in plan["capability_assessment"]["meaningful_gaps"]}
            self.assertEqual(gaps["sas-semantic-analysis"], "MISSING")
            self.assertEqual(gaps["sas-to-java-mapping"], "MISSING")
            self.assertTrue(target.exists())
            self.assertTrue((target / ".agent-commons.yaml").is_file())
            self.assertTrue(plan["safe_initialization_continues"])
            self.assertFalse(plan["capability_dependent_work_blocked"])
            state_path = target / ".agent-commons" / "external-discovery.json"
            for _ in range(100):
                if json.loads(state_path.read_text(encoding="utf-8"))["status"] != "running":
                    break
                time.sleep(0.02)

    def test_l_external_search_handoff_does_not_block_safe_setup(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            started = time.monotonic()
            result, plan = self.run_initializer(
                target, "--capability-gap-strategy", "search-external", "--external-source-scope", "all",
                "--external-discovery-snapshot", str(ROOT / "evals/fixtures/external/github-snapshot.json"),
            )
            elapsed = time.monotonic() - started
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(plan["search_handoff"]["workflow"], "search-external-capabilities")
            self.assertIn("SAS code semantic analysis agent skill", plan["search_handoff"]["queries"])
            self.assertTrue(plan["search_handoff"]["stop_after_findings"])
            self.assertTrue(plan["automatic_external_search"])
            self.assertLess(elapsed, 5)
            self.assertTrue(target.exists())
            self.assertTrue((target / ".agent-commons.yaml").is_file())
            self.assertTrue(plan["safe_initialization_continues"])
            self.assertFalse(plan["capability_dependent_work_blocked"])
            state_path = target / ".agent-commons" / "external-discovery.json"
            for _ in range(100):
                state = json.loads(state_path.read_text(encoding="utf-8"))
                if state["status"] != "running":
                    break
                time.sleep(0.02)
            self.assertIn(state["status"], {"completed", "partial-rate-limited", "partial-source-failure", "failed"})
            self.assertTrue((target / "analysis" / "external-capabilities.json").is_file())

    def test_matching_recent_external_discovery_is_reused_without_duplicate_launch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            arguments = (
                "--capability-gap-strategy", "search-external", "--external-source-scope", "all",
                "--source-technology", "COBOL and PL/I",
                "--target-technology", "Java 21/Spring Boot 4.x",
                "--external-discovery-snapshot", str(ROOT / "evals/fixtures/external/github-modernization-snapshot.json"),
            )
            first, _ = self.run_initializer(target, *arguments)
            self.assertEqual(first.returncode, 0, first.stderr)
            state_path = target / ".agent-commons" / "external-discovery.json"
            for _ in range(150):
                state = json.loads(state_path.read_text(encoding="utf-8"))
                if state["status"] != "running":
                    break
                time.sleep(0.02)
            completed_state = state_path.read_text(encoding="utf-8")
            second, plan = self.run_initializer(target, *arguments)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertTrue(plan["external_discovery"]["reused"])
            self.assertFalse(plan["external_discovery"]["blocked_by_active_run"])
            self.assertNotIn("pid", plan["external_discovery"])
            self.assertEqual(completed_state, state_path.read_text(encoding="utf-8"))

    def test_failed_external_discovery_is_not_reused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            arguments = (
                "--capability-gap-strategy", "search-external", "--external-source-scope", "all",
                "--external-discovery-snapshot", str(ROOT / "evals/fixtures/external/github-snapshot.json"),
            )
            first, _ = self.run_initializer(target, *arguments)
            self.assertEqual(first.returncode, 0, first.stderr)
            state_path = target / ".agent-commons" / "external-discovery.json"
            for _ in range(150):
                state = json.loads(state_path.read_text(encoding="utf-8"))
                if state["status"] != "running":
                    break
                time.sleep(0.02)
            state["status"] = "failed"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            second, plan = self.run_initializer(target, *arguments)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertFalse(plan["external_discovery"]["reused"])
            self.assertIn("pid", plan["external_discovery"])

    def test_active_project_lease_blocks_a_duplicate_different_request(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            initial, _ = self.run_initializer(target, "--capability-gap-strategy", "generic-only")
            self.assertEqual(initial.returncode, 0, initial.stderr)
            state_path = target / ".agent-commons" / "external-discovery.json"
            lock_path = target / ".agent-commons" / "external-discovery.lock"
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(json.dumps({"pid": os.getpid(), "request_key": "another-request"}), encoding="utf-8")
            second, plan = self.run_initializer(
                target,
                "--capability-gap-strategy", "search-external", "--external-source-scope", "all",
                "--external-discovery-snapshot", str(ROOT / "evals/fixtures/external/github-snapshot.json"),
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertFalse(plan["external_discovery"]["reused"])
            self.assertTrue(plan["external_discovery"]["blocked_by_active_run"])
            self.assertNotIn("pid", plan["external_discovery"])
            self.assertFalse(state_path.exists())

    def test_cobol_pli_to_java21_spring4_discovery_queries_are_safe_and_specific(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            result, plan = self.run_initializer(
                target,
                "--source-technology", "COBOL and PL/I",
                "--target-technology", "Java 21/Spring Boot 4.x",
                "--capability-gap-strategy", "search-external",
                "--external-source-scope", "all",
                "--external-discovery-snapshot", str(ROOT / "evals/fixtures/external/github-modernization-snapshot.json"),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            queries = " | ".join(plan["search_handoff"]["queries"])
            self.assertIn("COBOL", queries)
            self.assertIn("PL/I", queries)
            self.assertIn("Java 21/Spring Boot 4.x", queries)
            state_path = target / ".agent-commons" / "external-discovery.json"
            for _ in range(150):
                state = json.loads(state_path.read_text(encoding="utf-8"))
                if state["status"] != "running":
                    break
                time.sleep(0.02)
            self.assertIn(state["status"], {"completed", "partial-source-failure", "partial-rate-limited"})

    def test_slow_external_discovery_does_not_delay_core_initialization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            environment = dict(os.environ)
            environment["AGENT_COMMONS_EXTERNAL_DISCOVERY_DELAY_SECONDS"] = "1.0"
            started = time.monotonic()
            result = subprocess.run(
                ["python3", str(SCRIPT), "--root", str(target), "--name", "Slow discovery",
                 "--goal", "Extract requirements and prepare migration", "--done", "Parity checks pass",
                 "--scope", "legacy-migration,development", "--scale", "standard", "--runtime", "codex",
                 "--source-technology", "SAS", "--target-technology", "Java", "--no-git",
                 "--capability-gap-strategy", "search-external", "--external-source-scope", "all",
                 "--external-discovery-snapshot", str(ROOT / "evals/fixtures/external/github-snapshot.json")],
                capture_output=True, text=True, env=environment,
            )
            elapsed = time.monotonic() - started
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertLess(elapsed, 1.4)
            self.assertTrue((target / "dashboard" / "data.json").exists() or (target / ".agent-commons.yaml").exists())
            state_path = target / ".agent-commons" / "external-discovery.json"
            self.assertEqual(json.loads(state_path.read_text(encoding="utf-8"))["status"], "running")
            for _ in range(150):
                if json.loads(state_path.read_text(encoding="utf-8"))["status"] != "running":
                    break
                time.sleep(0.02)

    def test_m_only_explicitly_accepted_candidate_is_recorded_project_locally(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            acceptance = Path(temporary) / "accepted.json"
            acceptance.write_text(json.dumps({"accepted": [{
                "gap_id": "sas-semantic-analysis",
                "candidate_id": "candidate-a",
                "repository": "example/sas-analysis",
                "path": "skills/sas-analysis",
                "revision": "abc123",
                "license": "Apache-2.0",
                "trust": "CURATED",
                "reviewed_at": "2026-08-18",
                "integration": "methodology-only",
            }]}), encoding="utf-8")
            result, plan = self.run_initializer(
                target, "--accepted-external-file", str(acceptance),
                "--capability-gap-strategy", "project-local-later",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = self.manifest(target)
            self.assertIn('candidate_id: "candidate-a"', manifest)
            self.assertIn("scope: project-local", manifest)
            self.assertIn("relationship: INSPIRED-BY", manifest)
            self.assertNotIn("candidate-b", manifest)
            self.assertEqual(plan["accepted_external_candidates"], ["candidate-a"])
            self.assertFalse((target / ".agents" / "skills" / "sas-analysis").exists())

    def test_n_reject_all_can_continue_project_local_later(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            result, _ = self.run_initializer(
                target, "--capability-gap-strategy", "project-local-later",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = self.manifest(target)
            self.assertIn("resolution: project-local-later", manifest)
            instructions = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("before deep analysis begins", instructions)

    def test_o_official_only_scope_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result, plan = self.run_initializer(
                Path(temporary) / "project", "--capability-gap-strategy", "search-external",
                "--external-source-scope", "official",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(plan["external_source_scope"], "official")

    def test_q_partial_generic_coverage_exposes_only_material_choice_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            _, plan = self.run_initializer(Path(temporary) / "project")
            meaningful = plan["capability_assessment"]["meaningful_gaps"]
            self.assertTrue(any(entry["status"] == "PARTIALLY_COVERED" for entry in meaningful))
            self.assertFalse(any(entry["status"] == "OPTIONAL_GAP" for entry in meaningful))

    def test_r_source_and_target_generic_coverage_does_not_hide_bridge_gap(self) -> None:
        result = subprocess.run(
            ["python3", str(GAP_RESOLVER), "resolve", "--archetype", "legacy-migration,development",
             "--overlay", "evidence-traceability", "--source-technology", "SAS",
             "--target-technology", "Java", "--goal", "requirements migration", "--validation", "parity"],
            check=True,
            capture_output=True,
            text=True,
        )
        assessment = json.loads(result.stdout)
        bridge = next(entry for entry in assessment["meaningful_gaps"] if entry["dimension"] == "bridge")
        self.assertEqual(bridge["status"], "MISSING")
        self.assertTrue(bridge["covered_by"])

    def test_s_external_scripts_and_hooks_remain_review_only(self) -> None:
        skill = SEARCH_SKILL.read_text(encoding="utf-8")
        self.assertIn("scripts, hooks, plugins, MCPs", skill)
        self.assertIn("before any installation or execution", (ROOT / "skills" / "initialize-project" / "SKILL.md").read_text(encoding="utf-8"))

    def test_t_future_commons_candidate_is_only_project_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            acceptance = Path(temporary) / "accepted.json"
            acceptance.write_text(json.dumps({"accepted": [{
                "gap_id": "sas-semantic-analysis", "candidate_id": "candidate-a",
                "repository": "example/sas-analysis", "path": "skills/sas-analysis",
                "revision": "abc123", "license": "Apache-2.0", "trust": "OFFICIAL",
                "reviewed_at": "2026-08-18", "future_commons_candidate": True,
            }]}), encoding="utf-8")
            before = (ROOT / "catalog" / "capabilities.yaml").read_text(encoding="utf-8")
            result, _ = self.run_initializer(
                target, "--accepted-external-file", str(acceptance),
                "--capability-gap-strategy", "generic-only",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("future_commons_candidate: true", self.manifest(target))
            self.assertEqual((ROOT / "catalog" / "capabilities.yaml").read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
