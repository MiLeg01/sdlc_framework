#!/usr/bin/env python3
"""Public-sector client classification and output-language policy scenarios."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "skills" / "initialize-project" / "scripts"
INITIALIZER = SCRIPT_DIR / "initialize_project.py"
SHELL = ROOT / "skills" / "build-living-dashboard" / "assets" / "dashboard-shell.html"
sys.path.insert(0, str(SCRIPT_DIR))

from brief_intake import parse_brief  # noqa: E402
from initialize_project import detect_persisted_delivery  # noqa: E402


class PublicSectorDeliveryScenarios(unittest.TestCase):
    def parse(self, brief: str) -> dict[str, object]:
        return parse_brief(brief, ROOT)

    def test_austrian_government_brand_reference_selects_dashboard_policy(self) -> None:
        profile = self.parse(
            "legacy migration, SAS -> Java, requirements dashboard, "
            "client branding: https://federal-office.gv.at/corporate-design, "
            "audience: technical and management"
        )
        client = profile["known"]["client"]
        dashboard = profile["known"]["localization"]["dashboard"]
        self.assertEqual(client["public_sector_confidence"], "HIGH_CONFIDENCE")
        self.assertEqual((client["country"], client["locale"]), ("AT", "de-AT"))
        self.assertEqual(dashboard["languages"], ["de-AT", "en"])
        self.assertEqual(dashboard["default_language"], "de-AT")
        self.assertTrue(dashboard["language_switch"])
        self.assertNotIn("artifact.language", {item["id"] for item in profile["missing"]})

    def test_public_sector_sales_presentation_defaults_to_locale_only(self) -> None:
        profile = self.parse("sales presentation for a public-sector client in Austria")
        presentation = profile["known"]["localization"]["presentation"]
        self.assertEqual(presentation["languages"], ["de-AT"])
        self.assertEqual(presentation["default_language"], "de-AT")
        self.assertFalse(presentation["bilingual"])

    def test_explicit_english_presentation_override_wins(self) -> None:
        profile = self.parse(
            "sales presentation for a public-sector client in Austria. Presentation language: English"
        )
        presentation = profile["known"]["localization"]["presentation"]
        self.assertEqual(presentation["languages"], ["en"])
        self.assertEqual(presentation["source"], "explicit-project-instruction")

    def test_explicit_german_only_dashboard_override_wins(self) -> None:
        profile = self.parse(
            "technical dashboard for a public-sector client in Austria. Dashboard language: German only"
        )
        dashboard = profile["known"]["localization"]["dashboard"]
        self.assertEqual(dashboard["languages"], ["de-AT"])
        self.assertFalse(dashboard["language_switch"])

    def test_private_austrian_client_does_not_receive_public_defaults(self) -> None:
        profile = self.parse("technical dashboard for a private Austrian company")
        self.assertEqual(profile["known"]["client"]["public_sector_confidence"], "NOT_PUBLIC_SECTOR")
        self.assertFalse(profile["known"]["localization"]["dashboard"]["resolved"])
        self.assertIn("artifact.language", {item["id"] for item in profile["missing"]})

    def test_german_public_sector_client_uses_de_de(self) -> None:
        profile = self.parse("technical dashboard for a public-sector client in Germany")
        dashboard = profile["known"]["localization"]["dashboard"]
        self.assertEqual(dashboard["languages"], ["de-DE", "en"])
        self.assertEqual(dashboard["default_language"], "de-DE")

    def test_existing_project_persists_client_and_output_policies_separately(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".agent-commons.yaml").write_text(
                """client:
  organization: "Bundesamt"
  sector: public
  public_sector: true
  public_sector_confidence: CONFIRMED
  country: "AT"
  locale: "de-AT"
presentation:
  languages:
    - "de-AT"
  default_language: "de-AT"
  bilingual: false
dashboard:
  languages:
    - "de-AT"
    - "en"
  default_language: "de-AT"
  language_switch: true
localization:
  working_language: "en"
""",
                encoding="utf-8",
            )
            persisted = detect_persisted_delivery(root)
            result = subprocess.run(
                [
                    "python3", str(INITIALIZER), "--root", str(root), "--name", "Existing",
                    "--runtime", "codex", "--no-git", "--dry-run", "--brief",
                    "Create a sales presentation for this client",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            plan = json.loads(result.stdout)
        self.assertEqual(persisted["client"]["locale"], "de-AT")
        self.assertEqual(persisted["localization"]["dashboard"]["languages"], ["de-AT", "en"])
        self.assertEqual(persisted["localization"]["presentation"]["languages"], ["de-AT"])
        self.assertEqual(plan["inferred"]["presentation_languages"], ["de-AT"])
        self.assertNotIn("artifact.language", {item["id"] for item in plan["questions"]})

    def test_dashboard_shell_preserves_state_and_switches_without_reload(self) -> None:
        source = SHELL.read_text(encoding="utf-8")
        self.assertIn("client-artifact-language-change", source)
        self.assertIn("globalSearch", source)
        self.assertIn("detailDialog", source)
        self.assertIn("__LANGUAGE_SWITCH_BUTTONS__", source)
        self.assertIn("storageKey:delivery.storage_key", source)
        self.assertNotIn("location.reload", source)

    def test_research_working_language_can_remain_english_for_german_sales_output(self) -> None:
        profile = self.parse(
            "research then sales presentation for a public-sector client in Austria.\nWorking language: English"
        )
        localization = profile["known"]["localization"]
        self.assertEqual(localization["working_language"], "en")
        self.assertEqual(localization["presentation"]["languages"], ["de-AT"])

    def test_explicit_bilingual_sales_request_is_honored(self) -> None:
        profile = self.parse(
            "bilingual sales presentation for a public-sector client in Austria"
        )
        presentation = profile["known"]["localization"]["presentation"]
        self.assertEqual(presentation["languages"], ["de-AT", "en"])
        self.assertTrue(presentation["bilingual"])

    def test_initializer_selects_public_sector_overlay(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            command = [
                "python3", str(INITIALIZER), "--root", str(Path(temporary) / "project"),
                "--name", "Public client", "--runtime", "codex", "--no-git", "--dry-run",
                "--brief", (
                    "legacy migration, SAS -> Java, source ./client_input read-only, analysis only, "
                    "requirements dashboard, client branding: "
                    "https://federal-office.gv.at/corporate-design, "
                    "audience: technical and management"
                ),
            ]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        plan = json.loads(result.stdout)
        self.assertIn("public-sector-client-delivery", plan["composition"]["overlays"])
        self.assertEqual(plan["inferred"]["dashboard_languages"], ["de-AT", "en"])
        self.assertEqual(plan["unresolved_questions"], [])

    def test_public_sector_sales_composition_does_not_select_bilingual_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            command = [
                "python3", str(INITIALIZER), "--root", str(project),
                "--name", "Public sales", "--scope", "presentation", "--runtime", "codex",
                "--goal", "Earn the next decision", "--done", "Deck reviewed",
                "--presentation-topic", "Modernization", "--presentation-purpose", "sales",
                "--audience", "IT leadership", "--desired-outcome", "Approve discovery",
                "--html-artifact", "sales-presentation", "--brand-source", "neutral-premium",
                "--public-sector-client", "--client-country", "AT", "--no-git",
            ]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            presentation = (project / "presentation" / "index.html").read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        plan = json.loads(result.stdout)
        self.assertIn("public-sector-client-delivery", plan["composition"]["overlays"])
        self.assertNotIn("bilingual-client-delivery", plan["composition"]["overlays"])
        self.assertEqual(plan["inferred"]["presentation_languages"], ["de-AT"])
        self.assertFalse(plan["inferred"]["presentation_bilingual"])
        self.assertIn("Vertriebspräsentation", presentation)
        self.assertIn("Präsentation", presentation)
        self.assertIn("Accenture-Fallback", presentation)
        self.assertNotIn("sales-presentation", presentation)
        self.assertNotIn(">presentation<", presentation)
        self.assertNotIn("neutral-premium", presentation)
        self.assertNotIn("data-localization-locale", presentation)


if __name__ == "__main__":
    unittest.main()
