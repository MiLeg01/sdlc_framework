#!/usr/bin/env python3
"""Executable evaluations for client-artifact localization validation and runtime invariants."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "skills" / "localize-client-artifact" / "scripts" / "validate_localization.py"
EXAMPLE = ROOT / "skills" / "localize-client-artifact" / "assets" / "localization-manifest.example.json"
RUNTIME = ROOT / "skills" / "localize-client-artifact" / "assets" / "bilingual-runtime.js"


def digest(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def message(source: str, translated: str, **extra: object) -> dict[str, object]:
    return {
        "source": source,
        "source_hash": digest(source),
        "translations": {"de-AT": translated},
        **extra,
    }


class LocalizationValidatorScenarios(unittest.TestCase):
    def manifest(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "source_locale": "en",
            "target_locales": ["de-AT"],
            "default_locale": "de-AT",
            "fallback_locale": "en",
            "storage_key": "synthetic-language",
            "protected_terms": ["API"],
            "messages": {
                "dashboard.title": message("Modernization Overview", "Modernisierungsübersicht"),
                "action.open": message("Open API details", "API-Details öffnen"),
                "action.open.label": message("Open API details", "API-Details öffnen"),
                "technical.call": message(
                    "OrderService calls PaymentGateway through /payments/authorize.",
                    "Der OrderService ruft PaymentGateway über /payments/authorize auf.",
                    protected_terms=["OrderService", "PaymentGateway", "/payments/authorize"],
                ),
                "chart.summary": message("1,234.5 applications assessed", "1.234,5 Anwendungen bewertet"),
            },
        }

    def html(self) -> str:
        return """<!doctype html>
<html lang="de-AT"><head><title>Localized fixture</title></head><body>
<div class="language-switch" role="radiogroup" aria-label="Language">
  <button type="button" role="radio" data-localization-locale="de-AT" aria-label="Deutsch (Österreich)" aria-checked="true"><span aria-hidden="true">🇦🇹</span></button>
  <button type="button" role="radio" data-localization-locale="en" aria-label="English" aria-checked="false"><span aria-hidden="true">🇬🇧</span></button>
</div>
<h1 data-i18n="dashboard.title">Modernization Overview</h1>
<button data-i18n="action.open" data-i18n-attr="aria-label:action.open.label" aria-label="Open API details">Open API details</button>
<p data-i18n="technical.call">OrderService calls PaymentGateway through /payments/authorize.</p>
<p data-i18n="chart.summary">1,234.5 applications assessed</p>
</body></html>"""

    def run_validator(
        self,
        manifest: dict[str, object],
        *,
        html: str | None = None,
        strict_obsolete: bool = False,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = root / "localization.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            command = ["python3", str(VALIDATOR), "--manifest", str(manifest_path), "--json"]
            if html is not None:
                html_path = root / "artifact.html"
                html_path.write_text(html, encoding="utf-8")
                command += ["--html", str(html_path)]
            if strict_obsolete:
                command.append("--strict-obsolete")
            result = subprocess.run(command, capture_output=True, text=True)
            return result, json.loads(result.stdout)

    def test_example_manifest_is_valid(self) -> None:
        result = subprocess.run(
            ["python3", str(VALIDATOR), "--manifest", str(EXAMPLE), "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "PASS")

    def test_complete_dashboard_passes_with_flag_only_accessible_switch(self) -> None:
        result, report = self.run_validator(self.manifest(), html=self.html(), strict_obsolete=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report["missing_translation_count"], 0)
        self.assertEqual(report["stale_key_count"], 0)
        self.assertEqual(report["obsolete_key_count"], 0)

    def test_missing_translation_is_detected(self) -> None:
        manifest = self.manifest()
        manifest["messages"]["dashboard.title"]["translations"] = {}
        result, report = self.run_validator(manifest)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report["missing_translation_count"], 1)

    def test_stale_translation_is_detected_after_english_changes(self) -> None:
        manifest = self.manifest()
        manifest["messages"]["dashboard.title"]["source"] = "Updated modernization overview"
        result, report = self.run_validator(manifest)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report["stale_key_count"], 1)

    def test_technical_identifiers_and_numbers_are_preserved(self) -> None:
        valid_result, _ = self.run_validator(self.manifest())
        self.assertEqual(valid_result.returncode, 0)
        manifest = self.manifest()
        manifest["messages"]["technical.call"]["translations"]["de-AT"] = "Der BestellDienst ruft das Zahlungstor auf."
        manifest["messages"]["chart.summary"]["translations"]["de-AT"] = "1.244,5 Anwendungen bewertet"
        result, report = self.run_validator(manifest)
        self.assertNotEqual(result.returncode, 0)
        combined = " ".join(report["errors"])
        self.assertIn("protected terms", combined)
        self.assertIn("numeric meaning", combined)

    def test_unknown_html_key_and_flags_without_accessible_names_fail(self) -> None:
        html = self.html().replace(' aria-label="Deutsch (Österreich)"', "").replace(
            'data-i18n="dashboard.title"', 'data-i18n="dashboard.unknown"'
        )
        result, report = self.run_validator(self.manifest(), html=html)
        self.assertNotEqual(result.returncode, 0)
        combined = " ".join(report["errors"])
        self.assertIn("no accessible language name", combined)
        self.assertIn("unknown localization keys", combined)

    def test_runtime_is_offline_persistent_and_state_preserving_by_contract(self) -> None:
        source = RUNTIME.read_text(encoding="utf-8")
        self.assertIn("window.localStorage.getItem", source)
        self.assertIn("window.localStorage.setItem", source)
        self.assertIn("document.documentElement.lang", source)
        self.assertIn("client-artifact-language-change", source)
        self.assertIn("MutationObserver", source)
        self.assertNotIn("fetch(", source)
        self.assertNotIn("XMLHttpRequest", source)
        self.assertNotIn("location.reload", source)
        if shutil.which("node"):
            result = subprocess.run(["node", "--check", str(RUNTIME)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
