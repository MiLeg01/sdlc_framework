#!/usr/bin/env python3
"""Executable visual-product contract regressions for living dashboards."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER_PATH = ROOT / "skills" / "build-living-dashboard" / "scripts" / "build_dashboard.py"
VALIDATOR_PATH = ROOT / "skills" / "build-living-dashboard" / "scripts" / "validate_dashboard_visual.py"
EXAMPLE = ROOT / "skills" / "build-living-dashboard" / "assets" / "dashboard-data.example.json"
SHELL = ROOT / "skills" / "build-living-dashboard" / "assets" / "dashboard-shell.html"
CAPTURE = ROOT / "skills" / "build-living-dashboard" / "scripts" / "capture_dashboard_visual_qa.mjs"
BRAND_CAPTURE = ROOT / "skills" / "validate-visual-artifact" / "scripts" / "capture_brand_qa.mjs"
VISUAL_CAPTURE = ROOT / "skills" / "validate-visual-artifact" / "scripts" / "capture_visual_matrix.mjs"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_module("dashboard_builder_for_visual", BUILDER_PATH)
visual = load_module("dashboard_visual", VALIDATOR_PATH)


class DashboardVisualScenarios(unittest.TestCase):
    def test_hosted_browser_capture_disables_nested_chromium_sandbox(self) -> None:
        for path in (CAPTURE, BRAND_CAPTURE, VISUAL_CAPTURE):
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertIn('"--no-sandbox"', text)
                self.assertIn('"--disable-setuid-sandbox"', text)
                self.assertIn('"--disable-dev-shm-usage"', text)
                self.assertIn('"--disable-crash-reporter"', text)
                self.assertIn('"--no-zygote"', text)
                self.assertIn('"--disable-gpu"', text)

    def test_hosted_browser_capture_retries_transient_launch_failures(self) -> None:
        for path in (CAPTURE, BRAND_CAPTURE, VISUAL_CAPTURE):
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertIn("async function launchBrowser", text)
                self.assertIn("attempt <= 3", text)
                self.assertIn("await chromium.launch", text)
                self.assertIn("setTimeout(resolve", text)

    def render(self, root: Path) -> Path:
        data = builder.validate(json.loads(EXAMPLE.read_text(encoding="utf-8")))
        html = builder.render(data, SHELL.read_text(encoding="utf-8"))
        path = root / "index.html"
        path.write_text(html, encoding="utf-8")
        return path

    def test_canonical_template_passes_static_visual_fidelity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = self.render(Path(temporary))
            result = visual.validate(path)
        self.assertEqual(result["status"], "PASS", result["failures"])

    def test_generic_gradient_and_pill_drift_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = self.render(Path(temporary))
            drifted = path.read_text(encoding="utf-8")
            drifted = drifted.replace("background:var(--paper)}", "background:linear-gradient(#fff,#eee)}", 1)
            drifted = drifted.replace(".status-chip{", ".status-chip{border-radius:999px;", 1)
            path.write_text(drifted, encoding="utf-8")
            result = visual.validate(path)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("linear-gradient" in failure for failure in result["failures"]))
        self.assertTrue(any("unsupported pill styling" in failure for failure in result["failures"]))

    def test_visual_finesse_tokens_and_flat_register_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = self.render(Path(temporary))
            drifted = path.read_text(encoding="utf-8")
            drifted = drifted.replace("--space-section:", "--removed-space-section:", 1)
            drifted = drifted.replace(
                ".record-list{display:grid;grid-template-columns:1fr;gap:0;border-top:1px solid var(--line-strong)}",
                ".record-list{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}",
                1,
            )
            path.write_text(drifted, encoding="utf-8")
            result = visual.validate(path)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("required visual token is missing: --space-section" in failure
                            for failure in result["failures"]))
        self.assertTrue(any("required visual grammar fragment is missing" in failure
                            and ".record-list" in failure for failure in result["failures"]))

    def test_required_rendered_matrix_and_brand_gate_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.render(root)
            missing = visual.validate(path, require_qa=True)
            self.assertEqual(missing["status"], "FAIL")
            states = []
            for required in visual.load_contract()["required_rendered_states"]:
                screenshot = root / f"{required['id']}.png"
                screenshot.write_bytes(b"synthetic screenshot evidence")
                states.append({
                    "id": required["id"],
                    "status": "PASS",
                    "viewport": required["viewport"],
                    "locale": required.get("locale"),
                    "screenshot": screenshot.name,
                })
            manifest = {
                "schema_version": 2,
                "fingerprints": {
                    "design": visual.resolved_design_fingerprint(),
                    "html": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "data": builder.validate(json.loads(EXAMPLE.read_text(encoding="utf-8")))["fingerprint"],
                },
                "states": states,
                "results": {
                    "STRUCTURE_PASS": {"status": "PASS", "producer": "validate_dashboard_structure.py"},
                    "STATIC_HTML_PASS": {"status": "PASS", "producer": "validate_dashboard_visual.py"},
                    "VISUAL_QA_PASS": {"status": "PASS", "producer": "capture_dashboard_visual_qa.mjs"},
                    "ACCESSIBILITY_PASS": {"status": "PASS", "producer": "accessibility-review"},
                },
            }
            manifest_path = root / "visual-qa.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            passed = visual.validate(path, manifest_path, require_qa=True)
        self.assertEqual(passed["status"], "PASS", passed["failures"])
        self.assertEqual(passed["lifecycle_status"], "VALIDATED")

    def test_missing_visual_or_accessibility_gate_never_validates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.render(root)
            states = []
            for required in visual.load_contract()["required_rendered_states"]:
                screenshot = root / f"{required['id']}.png"
                screenshot.write_bytes(b"synthetic screenshot evidence")
                states.append({
                    "id": required["id"], "status": "PASS", "viewport": required["viewport"],
                    "locale": required.get("locale"), "screenshot": screenshot.name,
                })
            manifest = {
                "schema_version": 2,
                "fingerprints": {
                    "design": visual.resolved_design_fingerprint(),
                    "html": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "data": builder.validate(json.loads(EXAMPLE.read_text(encoding="utf-8")))["fingerprint"],
                },
                "states": states,
                "results": {
                    "STRUCTURE_PASS": {"status": "PASS", "producer": "structure-validator"},
                    "STATIC_HTML_PASS": {"status": "PASS", "producer": "static-validator"},
                    "VISUAL_QA_PASS": {"status": "PASS", "producer": "browser-capture"},
                },
            }
            manifest_path = root / "incomplete-qa.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = visual.validate(path, manifest_path, require_qa=True)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["lifecycle_status"], "BLOCKED")
        self.assertTrue(any("ACCESSIBILITY_PASS" in failure for failure in result["failures"]))


if __name__ == "__main__":
    unittest.main()
