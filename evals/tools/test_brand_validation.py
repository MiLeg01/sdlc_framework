#!/usr/bin/env python3
"""Executable validation scenarios for evidence-derived branded HTML."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DASHBOARD = ROOT / "skills/build-living-dashboard/scripts/build_dashboard.py"
VALIDATOR = ROOT / "skills/validate-visual-artifact/scripts/validate_html.py"
CAPTURE = ROOT / "skills/validate-visual-artifact/scripts/capture_brand_qa.mjs"
DATA = ROOT / "skills/build-living-dashboard/assets/dashboard-data.example.json"
PROFILE = ROOT / "evals/fixtures/branding/resolved-public-sector-profile.json"
DASHBOARD_ROLES = (
    "body", "header", "navigation", "link", "button", "focus", "status", "panel", "table", "footer",
)


def normalized_profile() -> dict:
    """Return the fixture profile with the fingerprints validate_html.py compares against."""
    sys.path.insert(0, str(ROOT / "skills/build-living-dashboard/scripts"))
    from brand_profile import validate_brand_profile

    return validate_brand_profile(json.loads(PROFILE.read_text(encoding="utf-8")))


class BrandValidationScenarios(unittest.TestCase):
    def generate(self, root: Path) -> Path:
        output = root / "index.html"
        subprocess.run([
            "python3", str(DASHBOARD), "--data", str(DATA), "--brand-profile", str(PROFILE),
            "--output", str(output),
        ], check=True, capture_output=True, text=True)
        return output

    def validate(self, html: Path, profile: Path = PROFILE) -> subprocess.CompletedProcess[str]:
        return subprocess.run([
            "python3", str(VALIDATOR), str(html), "--brand-profile", str(profile), "--json",
        ], capture_output=True, text=True)

    def qa_manifest(self, html: Path, responsive: list[dict] | None) -> Path:
        """Write a browser-free brand QA manifest so responsive policy is testable without Playwright."""
        profile = normalized_profile()
        viewports = [[1440, 1000], [768, 1024], [390, 844]]
        states = [
            {
                "id": name, "viewport": viewport, "brand_visible": True,
                "horizontal_overflow": False, "document_width": viewport[0],
                "viewport_width": viewport[0], "overflow_sources": [], "console_errors": [],
                "elements": [], "screenshot": "shot.png",
            }
            for name, viewport in zip(("desktop", "tablet", "mobile"), viewports)
        ]
        manifest = {
            "schema_version": 2,
            "artifact_kind": "dashboard",
            "profile_fingerprint": profile["profile_fingerprint"],
            "theme_fingerprint": profile["theme_fingerprint"],
            "asset_fingerprint": profile["asset_fingerprint"],
            "html_sha256": hashlib.sha256(html.read_bytes()).hexdigest(),
            "assets": {role: profile["assets"][role]["sha256"] for role in ("favicon", "logo")},
            "browser": {
                "engine": "chromium", "viewport": viewports[0],
                "viewports": viewports, "console_errors": [],
            },
            "elements": [
                {"role": role, "selector": role, "visible": True, "styles": {}}
                for role in DASHBOARD_ROLES
            ],
            "responsive": states if responsive is None else responsive,
            "browser_render": {"brand_visible": True, "screenshot": "shot.png"},
        }
        (html.parent / "shot.png").write_bytes(b"")
        path = html.parent / "brand-qa.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return path

    def validate_with_qa(self, html: Path, responsive: list[dict] | None) -> set[str]:
        manifest = self.qa_manifest(html, responsive)
        result = subprocess.run([
            "python3", str(VALIDATOR), str(html), "--brand-profile", str(PROFILE),
            "--brand-qa", str(manifest), "--json",
        ], capture_output=True, text=True)
        return {item["code"] for item in json.loads(result.stdout)["findings"]}

    def test_brand_qa_capture_records_a_mobile_reflow_state(self) -> None:
        text = CAPTURE.read_text(encoding="utf-8")
        self.assertIn('{id: "mobile", width: 390, height: 844}', text)
        self.assertIn("horizontal:", text)

    def test_complete_per_viewport_evidence_raises_no_responsive_finding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            codes = self.validate_with_qa(self.generate(Path(temporary)), None)
        self.assertNotIn("BRAND_RESPONSIVE_EVIDENCE_MISSING", codes)
        self.assertNotIn("BRAND_RESPONSIVE_OVERFLOW", codes)

    def test_desktop_only_brand_qa_is_rejected_as_incomplete_responsive_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            html = self.generate(Path(temporary))
            codes = self.validate_with_qa(html, [{
                "id": "desktop", "viewport": [1440, 1000], "brand_visible": True,
                "horizontal_overflow": False, "document_width": 1440, "viewport_width": 1440,
                "overflow_sources": [], "console_errors": [], "elements": [], "screenshot": "shot.png",
            }])
        self.assertIn("BRAND_RESPONSIVE_EVIDENCE_MISSING", codes)

    def test_mobile_horizontal_overflow_fails_brand_fidelity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            html = self.generate(Path(temporary))
            codes = self.validate_with_qa(html, [
                {
                    "id": "desktop", "viewport": [1440, 1000], "brand_visible": True,
                    "horizontal_overflow": False, "document_width": 1440, "viewport_width": 1440,
                    "overflow_sources": [], "console_errors": [], "elements": [], "screenshot": "shot.png",
                },
                {
                    "id": "mobile", "viewport": [390, 844], "brand_visible": True,
                    "horizontal_overflow": True, "document_width": 980, "viewport_width": 390,
                    "overflow_sources": [{"element": ".record-list"}], "console_errors": [],
                    "elements": [], "screenshot": "shot.png",
                },
            ])
        self.assertIn("BRAND_RESPONSIVE_OVERFLOW", codes)

    def test_identity_lost_at_mobile_width_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            html = self.generate(Path(temporary))
            codes = self.validate_with_qa(html, [{
                "id": "mobile", "viewport": [390, 844], "brand_visible": False,
                "horizontal_overflow": False, "document_width": 390, "viewport_width": 390,
                "overflow_sources": [], "console_errors": [], "elements": [], "screenshot": "shot.png",
            }])
        self.assertIn("BRAND_NOT_VISIBLY_EXPRESSED", codes)

    def test_generated_branded_dashboard_passes_profile_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = self.validate(self.generate(Path(temporary)))
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue(payload["checks"]["STATIC_HTML_PASS"])
        self.assertTrue(payload["checks"]["BRAND_PROFILE_CONSISTENT"])
        self.assertFalse(payload["checks"]["BRAND_FIDELITY_PASS"])
        self.assertIn("BRAND_VISUAL_QA_MISSING", {item["code"] for item in payload["findings"]})

    def test_token_tampering_fails_even_when_html_remains_structurally_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            html = self.generate(Path(temporary))
            text = html.read_text(encoding="utf-8").replace("--accent:#006f8b", "--accent:#123456")
            html.write_text(text, encoding="utf-8")
            result = self.validate(html)
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertIn("BRAND_TOKEN_MISMATCH", {item["code"] for item in payload["findings"]})

    def test_missing_profile_markers_fail_brand_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            html = self.generate(Path(temporary))
            text = html.read_text(encoding="utf-8").replace(' data-brand-status="resolved"', "")
            html.write_text(text, encoding="utf-8")
            result = self.validate(html)
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertIn("BRAND_MARKER_MISSING", {item["code"] for item in payload["findings"]})

    def test_stale_or_generic_required_profile_is_rejected_before_html_comparison(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            html = self.generate(root)
            profile = json.loads(PROFILE.read_text(encoding="utf-8"))
            profile["theme_fingerprint"] = "0" * 64
            stale = root / "stale-profile.json"
            stale.write_text(json.dumps(profile), encoding="utf-8")
            result = self.validate(html, stale)
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertIn("BRAND_PROFILE_INVALID", {item["code"] for item in payload["findings"]})


if __name__ == "__main__":
    unittest.main()
