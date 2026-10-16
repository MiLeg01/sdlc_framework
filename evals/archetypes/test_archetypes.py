#!/usr/bin/env python3
"""Executable archetype composition evaluations."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESOLVER = ROOT / "tools" / "resolve_archetypes.py"


class ArchetypeScenarios(unittest.TestCase):
    def resolve(self, *arguments: str) -> dict[str, object]:
        result = subprocess.run(
            ["python3", str(RESOLVER), "resolve", *arguments],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    def test_development_only(self) -> None:
        resolved = self.resolve("--archetype", "development")
        self.assertEqual(resolved["archetypes"], ["development"])
        self.assertIn("implement-ready-slice", resolved["capabilities"]["skills"])
        self.assertIn("specify-openspec-change", resolved["capabilities"]["skills"])
        self.assertIn("test-driven-development", resolved["capabilities"]["skills"])
        self.assertIn("verify-openspec-implementation", resolved["capabilities"]["skills"])
        self.assertNotIn("analyze-legacy-system", resolved["capabilities"]["skills"])
        self.assertNotIn("create-branded-html-artifact", resolved["capabilities"]["skills"])

    def test_development_default_selects_complete_openspec_family(self) -> None:
        resolved = self.resolve("--archetype", "development")
        skills = resolved["capabilities"]["skills"]
        expected = {
            "specify-openspec-change",
            "review-openspec-change",
            "implement-openspec-change",
            "verify-openspec-implementation",
            "complete-openspec-change",
        }
        self.assertTrue(expected <= set(skills))
        self.assertLess(skills.index("specify-openspec-change"), skills.index("implement-openspec-change"))

    def test_development_explicit_no_openspec_excludes_only_openspec_family(self) -> None:
        result = subprocess.run(
            ["python3", str(RESOLVER), "resolve", "--archetype", "development",
             *sum((["--exclude-skill", skill] for skill in (
                 "specify-openspec-change", "review-openspec-change", "implement-openspec-change",
                 "verify-openspec-implementation", "complete-openspec-change",
             )), [])],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        resolved = json.loads(result.stdout)
        self.assertNotIn("specify-openspec-change", resolved["capabilities"]["skills"])
        self.assertIn("test-driven-development", resolved["capabilities"]["skills"])
        self.assertEqual(len(resolved["excluded_skills"]), 5)

    def test_development_explicit_no_tdd_preserves_specification_family(self) -> None:
        resolved = json.loads(subprocess.run(
            ["python3", str(RESOLVER), "resolve", "--archetype", "development",
             "--exclude-skill", "test-driven-development"],
            cwd=ROOT, check=True, capture_output=True, text=True,
        ).stdout)
        self.assertIn("specify-openspec-change", resolved["capabilities"]["skills"])
        self.assertNotIn("test-driven-development", resolved["capabilities"]["skills"])
        self.assertEqual(resolved["excluded_skills"], ["test-driven-development"])

    def test_legacy_only(self) -> None:
        resolved = self.resolve("--archetype", "legacy-migration")
        self.assertEqual(
            resolved["capabilities"]["skills"],
            ["continue-project", "inventory-codebase", "analyze-legacy-system"],
        )
        self.assertNotIn("implement-ready-slice", resolved["capabilities"]["skills"])

    def test_legacy_analysis_requirements_stops_before_specification(self) -> None:
        resolved = self.resolve("--archetype", "legacy-migration", "--condition", "requirements-discovery")
        self.assertIn("derive-modernization-requirements", resolved["capabilities"]["skills"])
        self.assertNotIn("specify-openspec-change", resolved["capabilities"]["skills"])

    def test_legacy_migration_preparation_adds_openspec_without_tdd(self) -> None:
        resolved = self.resolve("--archetype", "legacy-migration", "--condition", "migration-openspec-preparation")
        self.assertIn("derive-modernization-requirements", resolved["capabilities"]["skills"])
        self.assertIn("specify-openspec-change", resolved["capabilities"]["skills"])
        self.assertNotIn("test-driven-development", resolved["capabilities"]["skills"])

    def test_presentation_without_medium_is_minimal(self) -> None:
        resolved = self.resolve("--archetype", "presentation")
        self.assertEqual(resolved["capabilities"]["skills"], [])

    def test_research_only_selects_deep_research_without_presentation(self) -> None:
        resolved = self.resolve("--archetype", "research")
        self.assertEqual(resolved["archetypes"], ["research"])
        self.assertIn("deep-research", resolved["capabilities"]["skills"])
        self.assertNotIn("sales-storytelling", resolved["capabilities"]["skills"])
        self.assertNotIn("create-branded-html-artifact", resolved["capabilities"]["skills"])
        self.assertNotIn("specify-openspec-change", resolved["capabilities"]["skills"])

    def test_presentation_does_not_trigger_openspec(self) -> None:
        resolved = self.resolve("--archetype", "presentation")
        openspec_skills = {skill for skill in resolved["capabilities"]["skills"] if "openspec" in skill}
        self.assertEqual(openspec_skills, set())

    def test_research_and_presentation_compose(self) -> None:
        resolved = self.resolve("--archetype", "research,presentation")
        self.assertEqual(resolved["archetypes"], ["research", "presentation"])
        self.assertEqual(resolved["capabilities"]["skills"], ["deep-research"])

    def test_research_sales_presentation_composes_as_overlay(self) -> None:
        resolved = self.resolve(
            "--archetype", "research,presentation",
            "--overlay", "sales-storytelling,branded-html",
        )
        skills = resolved["capabilities"]["skills"]
        for expected in (
            "deep-research", "sales-storytelling", "create-branded-html-artifact", "validate-visual-artifact",
        ):
            self.assertIn(expected, skills)
        self.assertEqual(len(skills), len(set(skills)))

    def test_legacy_and_development_compose(self) -> None:
        resolved = self.resolve("--archetype", "legacy-migration,development")
        skills = resolved["capabilities"]["skills"]
        self.assertEqual(
            skills,
            [
                "continue-project", "inventory-codebase", "analyze-legacy-system", "specify-openspec-change",
                "review-openspec-change", "implement-openspec-change", "implement-ready-slice",
                "test-driven-development", "mutation-testing", "verify-openspec-implementation",
                "complete-openspec-change",
            ],
        )

    def test_development_and_presentation_compose(self) -> None:
        resolved = self.resolve(
            "--archetype", "development,presentation",
            "--overlay", "branded-html",
        )
        skills = resolved["capabilities"]["skills"]
        self.assertIn("implement-ready-slice", skills)
        self.assertIn("create-branded-html-artifact", skills)
        self.assertNotIn("analyze-legacy-system", skills)

    def test_legacy_and_presentation_compose(self) -> None:
        resolved = self.resolve(
            "--archetype", "legacy-migration,presentation",
            "--overlay", "branded-html",
        )
        skills = resolved["capabilities"]["skills"]
        self.assertIn("analyze-legacy-system", skills)
        self.assertIn("create-branded-html-artifact", skills)
        self.assertNotIn("implement-ready-slice", skills)

    def test_full_hybrid_deduplicates_capabilities(self) -> None:
        resolved = self.resolve(
            "--archetype", "legacy-migration,development,presentation",
            "--overlay", "branded-html,evidence-traceability,living-dashboard",
        )
        skills = resolved["capabilities"]["skills"]
        self.assertEqual(len(skills), len(set(skills)))
        for expected in (
            "inventory-codebase",
            "analyze-legacy-system",
            "implement-ready-slice",
            "derive-modernization-requirements",
            "audit-delivery-traceability",
            "create-branded-html-artifact",
            "build-living-dashboard",
            "validate-visual-artifact",
        ):
            self.assertIn(expected, skills)

    def test_branded_html_composes_with_multiple_archetypes(self) -> None:
        for archetype in ("development", "legacy-migration", "presentation", "research"):
            with self.subTest(archetype=archetype):
                resolved = self.resolve(
                    "--archetype", archetype,
                    "--overlay", "branded-html",
                )
                self.assertIn("create-branded-html-artifact", resolved["capabilities"]["skills"])
                self.assertIn("validate-visual-artifact", resolved["capabilities"]["skills"])

    def test_sales_storytelling_is_compatible_with_research_and_presentation(self) -> None:
        for archetype in ("research", "presentation"):
            with self.subTest(archetype=archetype):
                resolved = self.resolve("--archetype", archetype, "--overlay", "sales-storytelling")
                self.assertIn("sales-storytelling", resolved["capabilities"]["skills"])

    def test_architecture_documentation_composes_with_every_archetype(self) -> None:
        for archetype in ("development", "legacy-migration", "presentation", "research"):
            with self.subTest(archetype=archetype):
                resolved = self.resolve("--archetype", archetype, "--overlay", "architecture-documentation")
                self.assertIn("create-technical-diagram", resolved["capabilities"]["skills"])
                self.assertIn("validate-diagram-model", resolved["capabilities"]["tools"])

    def test_architecture_view_conditions_select_only_requested_specialists(self) -> None:
        resolved = self.resolve(
            "--archetype", "development",
            "--overlay", "architecture-documentation",
            "--condition", "component-architecture-view,er-data-model-view,sequence-interaction-view",
        )
        skills = resolved["capabilities"]["skills"]
        for expected in (
            "create-technical-diagram",
            "create-component-architecture-diagram",
            "create-er-diagram",
            "create-sequence-diagram",
        ):
            self.assertIn(expected, skills)
        self.assertNotIn("create-class-diagram", skills)
        self.assertNotIn("create-data-flow-diagram", skills)

    def test_migration_roadmap_is_composed_not_a_specialist_skill(self) -> None:
        resolved = self.resolve(
            "--archetype", "legacy-migration",
            "--overlay", "architecture-documentation",
            "--condition", "migration-roadmap-view",
        )
        skills = resolved["capabilities"]["skills"]
        self.assertIn("create-system-landscape-diagram", skills)
        self.assertIn("create-component-architecture-diagram", skills)
        self.assertIn("plan-work", skills)
        self.assertNotIn("create-migration-roadmap-diagram", skills)

    def test_bilingual_client_delivery_composes_across_html_project_families(self) -> None:
        for archetype in ("development", "legacy-migration", "presentation", "research"):
            with self.subTest(archetype=archetype):
                resolved = self.resolve(
                    "--archetype", archetype,
                    "--overlay", "bilingual-client-delivery",
                )
                self.assertIn("localize-client-artifact", resolved["capabilities"]["skills"])
                self.assertIn("validate-visual-artifact", resolved["capabilities"]["skills"])
                self.assertIn("validate-client-localization", resolved["capabilities"]["tools"])

    def test_public_sector_client_delivery_composes_across_project_families(self) -> None:
        for archetype in ("development", "legacy-migration", "presentation", "research"):
            with self.subTest(archetype=archetype):
                resolved = self.resolve(
                    "--archetype", archetype,
                    "--overlay", "public-sector-client-delivery",
                )
                self.assertIn("validate-visual-artifact", resolved["capabilities"]["skills"])
                self.assertIn("accessibility-review", resolved["capabilities"]["skills"])

    def test_consulting_delivery_composes_without_runtime_or_firm_coupling(self) -> None:
        for archetype in ("development", "legacy-migration", "research"):
            with self.subTest(archetype=archetype):
                resolved = self.resolve(
                    "--archetype", archetype,
                    "--overlay", "consulting-delivery",
                )
                self.assertIn("manage-project-delivery", resolved["capabilities"]["skills"])
                self.assertIn("forecast-project-financials", resolved["capabilities"]["skills"])
                self.assertIn("financial-forecast-reviewer", resolved["capabilities"]["agents"])
                self.assertIn("analyze-project-delivery", resolved["capabilities"]["tools"])
                self.assertIn("calculate-project-financial-forecast", resolved["capabilities"]["tools"])

    def test_conditional_agent_requires_explicit_activation(self) -> None:
        plain = self.resolve("--archetype", "legacy-migration")
        activated = self.resolve(
            "--archetype", "legacy-migration",
            "--condition", "parallel-discovery",
        )
        self.assertEqual(plain["capabilities"]["agents"], [])
        self.assertEqual(activated["capabilities"]["agents"], ["legacy-discovery-specialist"])

    def test_tiny_suppresses_archetype_defaults_but_records_selection(self) -> None:
        resolved = self.resolve("--archetype", "development", "--scale", "tiny")
        self.assertEqual(resolved["archetypes"], ["development"])
        self.assertEqual(resolved["capabilities"]["skills"], [])

    def test_unknown_archetype_fails_without_fallback_invention(self) -> None:
        result = subprocess.run(
            ["python3", str(RESOLVER), "resolve", "--archetype", "unknown"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown archetype", result.stderr.lower())

    def test_contract_validation(self) -> None:
        result = subprocess.run(
            ["python3", str(RESOLVER), "validate"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("archetypes=4", result.stdout)
        self.assertIn("overlays=9", result.stdout)


if __name__ == "__main__":
    unittest.main()
