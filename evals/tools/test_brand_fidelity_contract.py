#!/usr/bin/env python3
"""Regression coverage for official brand resolution and rendered fidelity."""

from __future__ import annotations

import base64
import gzip
import hashlib
import json
import subprocess
import tempfile
import threading
import unittest
import zlib
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BRANDING_FIXTURES = ROOT / "evals/fixtures/branding"
SITE = BRANDING_FIXTURES / "mock-brand-site"
RESOLVER = ROOT / "skills/create-branded-html-artifact/scripts/resolve_brand_profile.py"
PRESENTATION_RENDERER = ROOT / "skills/create-branded-html-artifact/scripts/render_branded_html.py"
PRESENTATION_SHELL = ROOT / "skills/create-branded-html-artifact/assets/editorial-shell.html"
DASHBOARD = ROOT / "skills/build-living-dashboard/scripts/build_dashboard.py"
DASHBOARD_DATA = ROOT / "skills/build-living-dashboard/assets/dashboard-data.example.json"
VALIDATOR = ROOT / "skills/validate-visual-artifact/scripts/validate_html.py"
INITIALIZER = ROOT / "skills/initialize-project/scripts/initialize_project.py"
STRUCTURE_VALIDATOR = ROOT / "skills/build-living-dashboard/scripts/validate_dashboard_structure.py"
SEMANTIC_VALIDATOR = ROOT / "skills/build-living-dashboard/scripts/validate_dashboard_semantics.py"


class QuietHandler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/compressed-brand":
            source = (BRANDING_FIXTURES / "utility-variable-brand-site" / "index.html").read_text(encoding="utf-8")
            source = source.replace('href="site.css"', 'href="/utility-variable-brand-site/site.css"')
            source = source.replace('src="../semantic-brand-site/assets/logo.svg"', 'src="/semantic-brand-site/assets/logo.svg"')
            payload = gzip.compress(source.encode("utf-8"), mtime=0)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if self.path == "/deflate-brand":
            source = (BRANDING_FIXTURES / "utility-variable-brand-site" / "index.html").read_text(encoding="utf-8")
            source = source.replace('href="site.css"', 'href="/utility-variable-brand-site/site.css"')
            source = source.replace('src="../semantic-brand-site/assets/logo.svg"', 'src="/semantic-brand-site/assets/logo.svg"')
            payload = zlib.compress(source.encode("utf-8"))
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Encoding", "deflate")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if self.path == "/raw-deflate-brand":
            source = (BRANDING_FIXTURES / "utility-variable-brand-site" / "index.html").read_text(encoding="utf-8")
            source = source.replace('href="site.css"', 'href="/utility-variable-brand-site/site.css"')
            source = source.replace('src="../semantic-brand-site/assets/logo.svg"', 'src="/semantic-brand-site/assets/logo.svg"')
            compressor = zlib.compressobj(wbits=-zlib.MAX_WBITS)
            payload = compressor.compress(source.encode("utf-8")) + compressor.flush()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Encoding", "deflate")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if self.path == "/brand":
            self.send_response(302)
            self.send_header("Location", "/mock-brand-site/index.html")
            self.end_headers()
            return
        if self.path == "/semantic":
            self.send_response(302)
            self.send_header("Location", "/semantic-brand-site/index.html")
            self.end_headers()
            return
        if self.path == "/insufficient":
            self.send_response(302)
            self.send_header("Location", "/insufficient-brand-site/index.html")
            self.end_headers()
            return
        if self.path == "/unsafe":
            self.send_response(302)
            self.send_header("Location", "/unsafe-brand-site/index.html")
            self.end_headers()
            return
        if self.path == "/inaccessible":
            self.send_response(302)
            self.send_header("Location", "/inaccessible-brand-site/index.html")
            self.end_headers()
            return
        if self.path == "/cascade":
            self.send_response(302)
            self.send_header("Location", "/cascade-brand-site/index.html")
            self.end_headers()
            return
        if self.path == "/preview-only":
            self.send_response(302)
            self.send_header("Location", "/preview-only-brand-site/index.html")
            self.end_headers()
            return
        if self.path == "/mismatch":
            self.send_response(302)
            self.send_header("Location", "/mismatch-brand-site/index.html")
            self.end_headers()
            return
        if self.path == "/tuwien":
            self.send_response(302)
            self.send_header("Location", "/tuwien-inline-site/index.html")
            self.end_headers()
            return
        if self.path == "/unsafe-inline":
            self.send_response(302)
            self.send_header("Location", "/unsafe-inline-brand-site/index.html")
            self.end_headers()
            return
        if self.path == "/metadata-logo":
            self.send_response(302)
            self.send_header("Location", "/metadata-logo-brand-site/index.html")
            self.end_headers()
            return
        if self.path == "/core-only":
            self.send_response(302)
            self.send_header("Location", "/core-only-brand-site/index.html")
            self.end_headers()
            return
        if self.path == "/external-svg-reference":
            self.send_response(302)
            self.send_header("Location", "/external-svg-reference-site/index.html")
            self.end_headers()
            return
        if self.path == "/utility-variables":
            self.send_response(302)
            self.send_header("Location", "/utility-variable-brand-site/index.html")
            self.end_headers()
            return
        if self.path == "/role-remap":
            self.send_response(302)
            self.send_header("Location", "/role-remap-brand-site/index.html")
            self.end_headers()
            return
        if self.path == "/css-logo":
            self.send_response(302)
            self.send_header("Location", "/css-logo-brand-site/index.html")
            self.end_headers()
            return
        super().do_GET()

    def log_message(self, format: str, *args: object) -> None:
        pass


class BrandFidelityContractScenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        handler = partial(QuietHandler, directory=str(BRANDING_FIXTURES))
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}/brand"
        cls.semantic_url = f"http://127.0.0.1:{cls.server.server_port}/semantic"
        cls.insufficient_url = f"http://127.0.0.1:{cls.server.server_port}/insufficient"
        cls.unsafe_url = f"http://127.0.0.1:{cls.server.server_port}/unsafe"
        cls.inaccessible_url = f"http://127.0.0.1:{cls.server.server_port}/inaccessible"
        cls.cascade_url = f"http://127.0.0.1:{cls.server.server_port}/cascade"
        cls.preview_only_url = f"http://127.0.0.1:{cls.server.server_port}/preview-only"
        cls.mismatch_url = f"http://127.0.0.1:{cls.server.server_port}/mismatch"
        cls.tuwien_url = f"http://127.0.0.1:{cls.server.server_port}/tuwien"
        cls.unsafe_inline_url = f"http://127.0.0.1:{cls.server.server_port}/unsafe-inline"
        cls.metadata_logo_url = f"http://127.0.0.1:{cls.server.server_port}/metadata-logo"
        cls.core_only_url = f"http://127.0.0.1:{cls.server.server_port}/core-only"
        cls.external_svg_reference_url = f"http://127.0.0.1:{cls.server.server_port}/external-svg-reference"
        cls.utility_variables_url = f"http://127.0.0.1:{cls.server.server_port}/utility-variables"
        cls.compressed_url = f"http://127.0.0.1:{cls.server.server_port}/compressed-brand"
        cls.deflate_url = f"http://127.0.0.1:{cls.server.server_port}/deflate-brand"
        cls.raw_deflate_url = f"http://127.0.0.1:{cls.server.server_port}/raw-deflate-brand"
        cls.role_remap_url = f"http://127.0.0.1:{cls.server.server_port}/role-remap"
        cls.css_logo_url = f"http://127.0.0.1:{cls.server.server_port}/css-logo"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.thread.join(timeout=5)

    def resolve(self, root: Path, url: str | None = None, identifier: str = "northstar-civic") -> Path:
        profile = root / "brand-profile.json"
        result = subprocess.run([
            "python3", str(RESOLVER), "--url", url or self.url, "--output", str(profile),
            "--id", identifier, "--captured-at", "2026-08-19T00:00:00Z",
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return profile

    @staticmethod
    def embedded_bytes(record: dict) -> bytes:
        _, payload = record["data_uri"].split(",", 1)
        return base64.b64decode(payload)

    def validate(self, html: Path, profile: Path) -> dict:
        result = subprocess.run([
            "python3", str(VALIDATOR), str(html), "--brand-profile", str(profile), "--json",
        ], capture_output=True, text=True)
        return {"returncode": result.returncode, **json.loads(result.stdout)}

    @staticmethod
    def contrast(first: str, second: str) -> float:
        def luminance(value: str) -> float:
            channels = [int(value[index:index + 2], 16) / 255 for index in (1, 3, 5)]
            linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
            return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
        lighter, darker = sorted((luminance(first), luminance(second)), reverse=True)
        return (lighter + 0.05) / (darker + 0.05)

    def test_resolver_captures_exact_official_assets_manifest_styles_and_colours(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = json.loads(self.resolve(Path(temporary)).read_text(encoding="utf-8"))
        favicon = (SITE / "assets/favicon.svg").read_bytes()
        logo = (SITE / "assets/wordmark.svg").read_bytes()
        self.assertEqual(profile["schema_version"], 2)
        self.assertEqual(profile["status"], "resolved")
        self.assertEqual(profile["source"]["requested_url"], self.url)
        self.assertTrue(profile["source"]["resolved_url"].endswith("/index.html"))
        self.assertEqual(self.embedded_bytes(profile["assets"]["favicon"]), favicon)
        self.assertEqual(self.embedded_bytes(profile["assets"]["logo"]), logo)
        self.assertEqual(profile["assets"]["favicon"]["sha256"], hashlib.sha256(favicon).hexdigest())
        self.assertEqual(profile["assets"]["logo"]["sha256"], hashlib.sha256(logo).hexdigest())
        self.assertEqual(len(profile["source"]["stylesheets"]), 1)
        self.assertEqual(profile["source"]["manifest"]["media_type"], "application/manifest+json")
        observed = {item["value"] for item in profile["observed_colors"]}
        self.assertTrue(set(profile["theme"]["colors"].values()) <= observed)
        self.assertEqual(profile["resolution_method"], "css-custom-properties")
        self.assertTrue(all(item["decision"] == "observed" for item in profile["mappings"] if item["token"] != "theme.signature.style"))
        self.assertEqual(next(item for item in profile["mappings"] if item["token"] == "theme.signature.style")["decision"], "derived")
        self.assertTrue(all(item["confidence"] == "high" for item in profile["mappings"]))

    def test_compiled_css_semantic_fallback_resolves_complete_deterministic_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = json.loads(self.resolve(root, self.semantic_url, "harbor-public").read_text(encoding="utf-8"))
            second_path = root / "second.json"
            result = subprocess.run([
                "python3", str(RESOLVER), "--url", self.semantic_url, "--output", str(second_path),
                "--id", "harbor-public", "--captured-at", "2026-08-19T00:00:00Z",
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            second = json.loads(second_path.read_text(encoding="utf-8"))
        self.assertEqual(first["resolution_method"], "semantic-css")
        self.assertEqual(first["theme"]["colors"]["accent"], "#0078c4")
        self.assertEqual(first["theme"]["colors"]["header"], "#093c7d")
        self.assertEqual(first["theme"]["colors"]["risk"], "#e10031")
        self.assertEqual(first["theme"]["colors"]["good"], "#4a8255")
        self.assertEqual(first["theme"]["colors"]["muted"], "#727272")
        self.assertNotEqual(first["theme"]["colors"]["accent"], first["theme"]["colors"]["risk"])
        self.assertNotIn("#2056ae", first["theme"]["colors"].values())
        self.assertEqual(first["theme"]["typography"]["display"], "Roboto Condensed, Roboto, Arial, sans-serif")
        self.assertEqual(first["theme"]["typography"]["body"], "Roboto, Arial, sans-serif")
        self.assertEqual(first["profile_fingerprint"], second["profile_fingerprint"])
        self.assertEqual(first["asset_fingerprint"], second["asset_fingerprint"])
        self.assertEqual(first["theme_fingerprint"], second["theme_fingerprint"])
        self.assertEqual(
            {item["token"] for item in first["mappings"]},
            {f"theme.{group}.{key}" for group, values in first["theme"].items() for key in values},
        )
        self.assertTrue(all(item["decision"] in {"observed", "derived"} for item in first["mappings"]))
        self.assertTrue(all(item["confidence"] in {"high", "medium", "low"} for item in first["mappings"]))
        self.assertTrue(any(item["token"] == "theme.colors.risk_soft" for item in first["derived_tokens"]))
        for role in ("good", "link", "muted", "risk"):
            self.assertGreaterEqual(self.contrast(first["theme"]["colors"][role], first["theme"]["colors"]["surface"]), 4.5, role)
        self.assertGreaterEqual(self.contrast(first["theme"]["colors"]["on_dark"], first["theme"]["colors"]["accent"]), 4.5)

    def test_tuwien_inline_svg_and_compiled_css_resolve_without_fallback(self) -> None:
        fixture = BRANDING_FIXTURES / "tuwien-inline-site" / "index.html"
        source = fixture.read_text(encoding="utf-8")
        expected_logo = source[source.index("<svg role=\"img\""):source.index("</svg>") + len("</svg>")].encode("utf-8")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            profile_path = self.resolve(root, self.tuwien_url, "tu-wien")
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            dashboard = root / "dashboard.html"
            presentation = root / "presentation.html"
            subprocess.run([
                "python3", str(DASHBOARD), "--data", str(DASHBOARD_DATA),
                "--brand-profile", str(profile_path), "--output", str(dashboard),
            ], check=True, capture_output=True, text=True)
            subprocess.run([
                "python3", str(PRESENTATION_RENDERER), "--template", str(PRESENTATION_SHELL),
                "--brand-profile", str(profile_path), "--output", str(presentation),
            ], check=True, capture_output=True, text=True)
            rendered_artifacts = (dashboard.read_text(encoding="utf-8"), presentation.read_text(encoding="utf-8"))

        logo_bytes = self.embedded_bytes(profile["assets"]["logo"])
        self.assertEqual(profile["status"], "resolved")
        self.assertEqual(profile["resolution_method"], "semantic-css")
        self.assertEqual(profile["theme"]["colors"]["accent"], "#006699")
        self.assertEqual(profile["theme"]["colors"]["risk"], "#e61e32")
        self.assertEqual(logo_bytes, expected_logo)
        self.assertEqual(profile["assets"]["logo"]["sha256"], hashlib.sha256(expected_logo).hexdigest())
        self.assertTrue(profile["assets"]["logo"]["source_url"].endswith("#inline-svg-logo-1"))
        self.assertIn("#006699", profile["theme"]["colors"].values())
        self.assertIn("#084f72", profile["theme"]["colors"].values())
        self.assertNotIn("#a100ff", profile["theme"]["colors"].values())
        observed = {item["value"] for item in profile["observed_colors"]}
        self.assertIn("#28a745", observed)
        self.assertIn("#e61e32", observed)
        for role in ("good", "risk"):
            self.assertGreaterEqual(self.contrast(profile["theme"]["colors"][role], profile["theme"]["colors"]["surface"]), 4.5)
        for rendered in rendered_artifacts:
            self.assertIn(profile["assets"]["logo"]["data_uri"], rendered)
            self.assertIn(profile["theme_fingerprint"], rendered)
            self.assertNotIn('data-brand-id="accenture-fallback"', rendered)

    def test_unsafe_inline_svg_logo_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "blocked.json"
            result = subprocess.run([
                "python3", str(RESOLVER), "--url", self.unsafe_inline_url, "--output", str(output),
                "--id", "unsafe-inline", "--captured-at", "2026-08-19T00:00:00Z",
            ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("identity.logo", result.stdout + result.stderr)
        self.assertIn("unsafe", (result.stdout + result.stderr).lower())

    def test_inline_svg_logo_with_external_reference_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "blocked.json"
            result = subprocess.run([
                "python3", str(RESOLVER), "--url", self.external_svg_reference_url, "--output", str(output),
                "--id", "external-svg-reference", "--captured-at", "2026-08-19T00:00:00Z",
            ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("identity.logo", result.stdout + result.stderr)
        self.assertIn("externally referenced", (result.stdout + result.stderr).lower())

    def test_explicit_logo_metadata_is_a_supported_official_identity_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = json.loads(self.resolve(Path(temporary), self.metadata_logo_url, "metadata-civic").read_text(encoding="utf-8"))
        self.assertTrue(profile["assets"]["logo"]["source_url"].endswith("/semantic-brand-site/assets/logo.svg"))
        self.assertEqual(profile["assets"]["favicon"]["sha256"], profile["assets"]["logo"]["sha256"])
        self.assertTrue(any("reused" in warning for warning in profile["source"]["capture_warnings"]))

    def test_core_identity_does_not_fall_back_when_optional_tokens_are_absent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = json.loads(self.resolve(Path(temporary), self.core_only_url, "core-only").read_text(encoding="utf-8"))
        self.assertEqual(profile["status"], "resolved")
        self.assertEqual(profile["theme"]["colors"]["accent"], "#005db4")
        mappings = {item["token"]: item for item in profile["mappings"]}
        for token in ("theme.colors.good", "theme.colors.risk", "theme.geometry.radius", "theme.typography.body"):
            self.assertEqual(mappings[token]["decision"], "derived")
            self.assertIn(mappings[token]["confidence"], {"low", "medium"})

    def test_arbitrary_css_variables_are_resolved_through_visible_semantic_selectors(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = json.loads(self.resolve(Path(temporary), self.utility_variables_url, "utility-variable-brand").read_text(encoding="utf-8"))
        self.assertEqual(profile["status"], "resolved")
        self.assertEqual(profile["resolution_method"], "semantic-css")
        self.assertEqual(profile["theme"]["colors"]["accent"], "#005c99")
        self.assertEqual(profile["theme"]["colors"]["ink"], "#032138")
        self.assertEqual(profile["theme"]["colors"]["header"], "#032138")
        accent_evidence = next(item for item in profile["observed_colors"] if item["value"] == "#005c99")
        self.assertTrue(any("visible" in usage and "primary" in usage for usage in accent_evidence["usages"]))

    def test_gzip_encoded_official_html_is_decoded_before_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = json.loads(self.resolve(Path(temporary), self.compressed_url, "compressed-brand").read_text(encoding="utf-8"))
        self.assertEqual(profile["status"], "resolved")
        self.assertEqual(profile["theme"]["colors"]["accent"], "#005c99")
        self.assertTrue(profile["assets"]["logo"]["source_url"].endswith("/semantic-brand-site/assets/logo.svg"))

    def test_deflate_encoded_official_html_is_decoded_before_discovery(self) -> None:
        for url, identifier in ((self.deflate_url, "deflate-brand"), (self.raw_deflate_url, "raw-deflate-brand")):
            with self.subTest(identifier=identifier), tempfile.TemporaryDirectory() as temporary:
                profile = json.loads(self.resolve(Path(temporary), url, identifier).read_text(encoding="utf-8"))
            self.assertEqual(profile["status"], "resolved")
            self.assertEqual(profile["theme"]["colors"]["accent"], "#005c99")

    def test_inaccessible_observed_link_and_focus_are_remapped_without_losing_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = json.loads(self.resolve(Path(temporary), self.role_remap_url, "role-remap-brand").read_text(encoding="utf-8"))
        colors = profile["theme"]["colors"]
        mappings = {item["token"]: item for item in profile["mappings"]}
        self.assertEqual(profile["status"], "resolved")
        self.assertEqual(colors["accent"], "#008c95")
        self.assertEqual(colors["surface"], "#ffffff")
        self.assertGreaterEqual(self.contrast(colors["link"], colors["surface"]), 4.5)
        self.assertGreaterEqual(self.contrast(colors["focus"], colors["surface"]), 3.0)
        self.assertIn(mappings["theme.colors.link"]["decision"], {"observed", "derived"})
        self.assertIn(mappings["theme.colors.focus"]["decision"], {"observed", "derived"})
        self.assertTrue(any(item["value"] == "#72cbd1" for item in profile["observed_colors"]))

    def test_visible_css_background_logo_is_safely_embedded_as_official_identity(self) -> None:
        expected = (BRANDING_FIXTURES / "css-logo-brand-site" / "logo.svg").read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            profile = json.loads(self.resolve(Path(temporary), self.css_logo_url, "css-logo-brand").read_text(encoding="utf-8"))
        self.assertEqual(self.embedded_bytes(profile["assets"]["logo"]), expected)
        self.assertEqual(profile["assets"]["logo"]["sha256"], hashlib.sha256(expected).hexdigest())
        self.assertIn("site.css#", profile["assets"]["logo"]["source_url"])

    def test_custom_property_fast_path_honours_stylesheet_cascade_and_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = json.loads(self.resolve(Path(temporary), self.cascade_url, "cascade-civic").read_text(encoding="utf-8"))
        self.assertEqual(profile["resolution_method"], "css-custom-properties")
        self.assertEqual(profile["theme"]["colors"]["accent"], "#0078c4")
        mapping = next(item for item in profile["mappings"] if item["token"] == "theme.colors.accent")
        self.assertTrue(mapping["source_ref"].endswith("/cascade-brand-site/override.css"))

    def test_missing_optional_stylesheet_is_recorded_but_does_not_block_complete_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = json.loads(self.resolve(Path(temporary), self.semantic_url, "harbor-public").read_text(encoding="utf-8"))
        self.assertEqual(profile["status"], "resolved")
        self.assertTrue(any("optional-missing.css" in warning for warning in profile["source"]["capture_warnings"]))

    def test_social_preview_is_not_used_as_logo_when_official_favicon_identity_is_available(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = json.loads(self.resolve(Path(temporary), self.preview_only_url, "preview-only").read_text(encoding="utf-8"))
        self.assertTrue(profile["assets"]["logo"]["source_url"].endswith("/semantic-brand-site/assets/favicon.svg"))
        self.assertFalse(profile["assets"]["logo"]["source_url"].endswith("/semantic-brand-site/assets/logo.svg"))

    def test_declared_asset_media_type_must_match_exact_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "blocked.json"
            result = subprocess.run([
                "python3", str(RESOLVER), "--url", self.mismatch_url, "--output", str(output),
                "--id", "mismatched-asset", "--captured-at", "2026-08-19T00:00:00Z",
            ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("bytes do not match declared media type image/png", result.stdout + result.stderr)

    def test_insufficient_core_palette_reports_actionable_missing_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "blocked.json"
            result = subprocess.run([
                "python3", str(RESOLVER), "--url", self.insufficient_url, "--output", str(output),
                "--id", "insufficient-brand", "--captured-at", "2026-08-19T00:00:00Z",
            ], capture_output=True, text=True)
        diagnostics = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("theme.colors.accent", diagnostics)
        self.assertIn("primary controls, navigation, or links", diagnostics)
        self.assertNotIn("missing official CSS custom property", diagnostics)
        self.assertIn("Action:", diagnostics)

    def test_mismatched_asset_hashes_are_rejected_for_each_identity_asset(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = json.loads(self.resolve(root, self.semantic_url, "harbor-public").read_text(encoding="utf-8"))
            for role in ("favicon", "logo"):
                with self.subTest(role=role):
                    payload = json.loads(json.dumps(original))
                    payload["assets"][role]["sha256"] = "0" * 64
                    invalid = root / f"invalid-{role}.json"
                    invalid.write_text(json.dumps(payload), encoding="utf-8")
                    output = root / f"invalid-{role}.html"
                    result = subprocess.run([
                        "python3", str(DASHBOARD), "--data", str(DASHBOARD_DATA),
                        "--brand-profile", str(invalid), "--output", str(output),
                    ], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn(f"assets.{role} embedded bytes do not match sha256", result.stderr)
                    self.assertIn('data-brand-id="accenture-fallback"', output.read_text(encoding="utf-8"))

    def test_profile_validator_rejects_mismatched_asset_media_and_inaccessible_text_roles(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = json.loads(self.resolve(root, self.semantic_url, "harbor-public").read_text(encoding="utf-8"))
            cases = {}
            mismatched = json.loads(json.dumps(original))
            mismatched["assets"]["favicon"]["media_type"] = "image/png"
            mismatched["assets"]["favicon"]["data_uri"] = mismatched["assets"]["favicon"]["data_uri"].replace("data:image/svg+xml", "data:image/png", 1)
            cases["media"] = (mismatched, "bytes do not match media_type image/png")
            inaccessible = json.loads(json.dumps(original))
            inaccessible["theme"]["colors"]["muted"] = "#9e9e9e"
            cases["contrast"] = (inaccessible, "must meet 4.5:1 contrast against surface")
            for name, (payload, diagnostic) in cases.items():
                with self.subTest(name=name):
                    for fingerprint in ("profile_fingerprint", "theme_fingerprint", "asset_fingerprint"):
                        payload.pop(fingerprint, None)
                    invalid = root / f"invalid-{name}.json"
                    invalid.write_text(json.dumps(payload), encoding="utf-8")
                    output = root / f"invalid-{name}.html"
                    result = subprocess.run([
                        "python3", str(DASHBOARD), "--data", str(DASHBOARD_DATA),
                        "--brand-profile", str(invalid), "--output", str(output),
                    ], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn(diagnostic, result.stderr)
                    self.assertIn('data-brand-id="accenture-fallback"', output.read_text(encoding="utf-8"))

    def test_profile_requires_confidence_and_observed_or_derived_classification_for_every_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = json.loads(self.resolve(root, self.semantic_url, "harbor-public").read_text(encoding="utf-8"))
            cases = {
                "mapping-decision": ("mappings", 0, "decision"),
                "mapping-confidence": ("mappings", 0, "confidence"),
                "observed-confidence": ("observed_colors", 0, "confidence"),
                "derived-confidence": ("derived_tokens", 0, "confidence"),
            }
            for name, (collection, index, field) in cases.items():
                with self.subTest(name=name):
                    payload = json.loads(json.dumps(original))
                    payload[collection][index].pop(field)
                    for fingerprint in ("profile_fingerprint", "theme_fingerprint", "asset_fingerprint"):
                        payload.pop(fingerprint, None)
                    invalid = root / f"{name}.json"
                    invalid.write_text(json.dumps(payload), encoding="utf-8")
                    output = root / f"{name}.html"
                    result = subprocess.run([
                        "python3", str(DASHBOARD), "--data", str(DASHBOARD_DATA),
                        "--brand-profile", str(invalid), "--output", str(output),
                    ], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn(field, result.stderr)
                    self.assertIn('data-brand-id="accenture-fallback"', output.read_text(encoding="utf-8"))

    def test_unsafe_official_asset_blocks_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "blocked.json"
            result = subprocess.run([
                "python3", str(RESOLVER), "--url", self.unsafe_url, "--output", str(output),
                "--id", "unsafe-brand", "--captured-at", "2026-08-19T00:00:00Z",
            ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("identity.logo", result.stdout + result.stderr)
        self.assertIn("unsafe", (result.stdout + result.stderr).lower())

    def test_inaccessible_official_asset_blocks_resolution_with_asset_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "blocked.json"
            result = subprocess.run([
                "python3", str(RESOLVER), "--url", self.inaccessible_url, "--output", str(output),
                "--id", "inaccessible-brand", "--captured-at", "2026-08-19T00:00:00Z",
            ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("identity.logo", result.stdout + result.stderr)
        self.assertIn("404", result.stdout + result.stderr)

    def test_initializer_passes_one_profile_and_exact_assets_to_both_renderers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            profile = self.resolve(root, self.semantic_url, "harbor-public")
            target = root / "project"
            result = subprocess.run([
                "python3", str(INITIALIZER), "--root", str(target), "--name", "Harbor delivery",
                "--scope", "development,presentation", "--runtime", "codex", "--no-git",
                "--goal", "Create one coordinated client delivery", "--done", "Both artifacts validate",
                "--html-artifact", "combination", "--brand-source", self.semantic_url,
                "--brand-profile-file", str(profile), "--presentation-topic", "Delivery",
                "--presentation-purpose", "executive", "--audience", "client leadership",
                "--desired-outcome", "Approve delivery", "--external-research", "skip",
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            dashboard = target / "dashboard/index.html"
            dashboard_data = target / "dashboard/data.json"
            presentation = target / "presentation/index.html"
            persisted_profile = target / "brand/profile.json"
            self.assertTrue(dashboard.is_file())
            self.assertTrue(presentation.is_file())
            resolved = json.loads(persisted_profile.read_text(encoding="utf-8"))
            dashboard_text = dashboard.read_text(encoding="utf-8")
            presentation_text = presentation.read_text(encoding="utf-8")
            for fingerprint in ("profile_fingerprint", "theme_fingerprint", "asset_fingerprint"):
                self.assertIn(str(resolved[fingerprint]), dashboard_text)
                self.assertIn(str(resolved[fingerprint]), presentation_text)
            for role in ("favicon", "logo"):
                self.assertIn(resolved["assets"][role]["data_uri"], dashboard_text)
                self.assertIn(resolved["assets"][role]["data_uri"], presentation_text)
            drift = subprocess.run([
                "python3", str(DASHBOARD), "--data", str(dashboard_data),
                "--brand-profile", str(persisted_profile), "--output", str(dashboard), "--check",
            ], capture_output=True, text=True)
            structure = subprocess.run([
                "python3", str(STRUCTURE_VALIDATOR), "--html", str(dashboard), "--data", str(dashboard_data),
            ], capture_output=True, text=True)
            semantics = subprocess.run([
                "python3", str(SEMANTIC_VALIDATOR), "--data", str(dashboard_data),
                "--peer-html", str(presentation),
            ], capture_output=True, text=True)
            static = subprocess.run([
                "python3", str(VALIDATOR), str(dashboard), "--brand-profile", str(persisted_profile),
                "--peer-html", str(presentation), "--json",
            ], capture_output=True, text=True)
            static_payload = json.loads(static.stdout)
        self.assertEqual(drift.returncode, 0, drift.stdout + drift.stderr)
        self.assertEqual(structure.returncode, 0, structure.stdout + structure.stderr)
        self.assertEqual(semantics.returncode, 0, semantics.stdout + semantics.stderr)
        self.assertTrue(static_payload["checks"]["STATIC_HTML_PASS"])
        self.assertTrue(static_payload["checks"]["BRAND_PROFILE_CONSISTENT"])

    def test_dashboard_and_presentation_consume_identical_profile_assets_and_palette(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            profile = self.resolve(root)
            dashboard = root / "dashboard.html"
            presentation = root / "presentation.html"
            subprocess.run([
                "python3", str(DASHBOARD), "--data", str(DASHBOARD_DATA),
                "--brand-profile", str(profile), "--output", str(dashboard),
            ], check=True, capture_output=True, text=True)
            subprocess.run([
                "python3", str(PRESENTATION_RENDERER), "--template", str(PRESENTATION_SHELL),
                "--brand-profile", str(profile), "--output", str(presentation),
            ], check=True, capture_output=True, text=True)
            dashboard_result = self.validate(dashboard, profile)
            presentation_result = self.validate(presentation, profile)
            dashboard_text = dashboard.read_text(encoding="utf-8")
            presentation_text = presentation.read_text(encoding="utf-8")
            resolved = json.loads(profile.read_text(encoding="utf-8"))
        self.assertTrue(dashboard_result["checks"]["BRAND_PROFILE_CONSISTENT"])
        self.assertTrue(presentation_result["checks"]["BRAND_PROFILE_CONSISTENT"])
        for role in ("favicon", "logo"):
            data_uri = resolved["assets"][role]["data_uri"]
            self.assertIn(data_uri, dashboard_text)
            self.assertIn(data_uri, presentation_text)
        for value in set(resolved["theme"]["colors"].values()):
            self.assertIn(value, dashboard_text)
            self.assertIn(value, presentation_text)

    def test_presentation_renderer_creates_html_with_accenture_fallback_when_profile_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for profile_argument in ([], ["--brand-profile", str(root / "missing-brand.json")]):
                output = root / ("without-profile.html" if not profile_argument else "unreadable-profile.html")
                result = subprocess.run([
                    "python3", str(PRESENTATION_RENDERER), "--template", str(PRESENTATION_SHELL),
                    *profile_argument, "--output", str(output),
                ], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                rendered = output.read_text(encoding="utf-8")
                self.assertIn('data-brand-id="accenture-fallback"', rendered)
                self.assertIn('data-brand-status="fallback"', rendered)

    def test_dashboard_renderer_creates_html_with_accenture_fallback_when_profile_is_unreadable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "dashboard.html"
            result = subprocess.run([
                "python3", str(DASHBOARD), "--data", str(DASHBOARD_DATA),
                "--brand-profile", str(root / "missing-brand.json"), "--output", str(output),
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            rendered = output.read_text(encoding="utf-8")
            self.assertIn('data-brand-id="accenture-fallback"', rendered)
            self.assertIn('data-brand-status="fallback"', rendered)

    def test_empty_synthetic_favicon_placeholder_logo_and_generic_palette_fail_fidelity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            profile = self.resolve(root)
            dashboard = root / "dashboard.html"
            subprocess.run([
                "python3", str(DASHBOARD), "--data", str(DASHBOARD_DATA),
                "--brand-profile", str(profile), "--output", str(dashboard),
            ], check=True, capture_output=True, text=True)
            original = dashboard.read_text(encoding="utf-8")
            cases = {
                "empty-favicon": original.replace(json.loads(profile.read_text())["assets"]["favicon"]["data_uri"], "data:,", 1),
                "placeholder-logo": original.replace("data-brand-logo", "data-brand-placeholder-logo", 1).replace("<img", '<span class="brand-mark">AC</span><img', 1),
                "generic-palette": original.replace("</style>", ".forced-generic{background:#202a2b;color:#f4f6f3}</style>", 1),
            }
            codes = {}
            for name, source in cases.items():
                path = root / f"{name}.html"
                path.write_text(source, encoding="utf-8")
                result = self.validate(path, profile)
                self.assertEqual(result["returncode"], 1, name)
                codes[name] = {item["code"] for item in result["findings"]}
        self.assertIn("BRAND_FAVICON_MISMATCH", codes["empty-favicon"])
        self.assertIn("BRAND_LOGO_PLACEHOLDER", codes["placeholder-logo"])
        self.assertIn("BRAND_GENERIC_PALETTE_RESIDUAL", codes["generic-palette"])

    def test_token_consistency_alone_does_not_claim_fidelity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            profile = self.resolve(root)
            dashboard = root / "dashboard.html"
            subprocess.run([
                "python3", str(DASHBOARD), "--data", str(DASHBOARD_DATA),
                "--brand-profile", str(profile), "--output", str(dashboard),
            ], check=True, capture_output=True, text=True)
            result = self.validate(dashboard, profile)
        self.assertTrue(result["checks"]["STATIC_HTML_PASS"])
        self.assertTrue(result["checks"]["BRAND_PROFILE_CONSISTENT"])
        self.assertFalse(result["checks"]["BRAND_FIDELITY_PASS"])
        self.assertFalse(result["checks"]["VISUAL_QA_PASS"])

    def test_synthetic_required_asset_is_rejected_as_client_brand_and_uses_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            profile = self.resolve(root)
            payload = json.loads(profile.read_text(encoding="utf-8"))
            payload["assets"]["favicon"]["source_kind"] = "generated"
            profile.write_text(json.dumps(payload), encoding="utf-8")
            dashboard = root / "dashboard.html"
            result = subprocess.run([
                "python3", str(DASHBOARD), "--data", str(DASHBOARD_DATA),
                "--brand-profile", str(profile), "--output", str(dashboard),
            ], capture_output=True, text=True)
            rendered = dashboard.read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 0)
        self.assertIn("official", result.stdout + result.stderr)
        self.assertIn("using Accenture fallback", result.stderr)
        self.assertIn('data-brand-id="accenture-fallback"', rendered)

    def test_peer_artifact_with_different_brand_assets_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            profile = self.resolve(root)
            dashboard = root / "dashboard.html"
            presentation = root / "presentation.html"
            subprocess.run([
                "python3", str(DASHBOARD), "--data", str(DASHBOARD_DATA),
                "--brand-profile", str(profile), "--output", str(dashboard),
            ], check=True, capture_output=True, text=True)
            subprocess.run([
                "python3", str(PRESENTATION_RENDERER), "--template", str(PRESENTATION_SHELL),
                "--brand-profile", str(profile), "--output", str(presentation),
            ], check=True, capture_output=True, text=True)
            source = presentation.read_text(encoding="utf-8")
            source = source.replace(json.loads(profile.read_text())["assets"]["logo"]["data_uri"], "data:image/svg+xml;base64,PHN2Zy8+")
            presentation.write_text(source, encoding="utf-8")
            result = subprocess.run([
                "python3", str(VALIDATOR), str(dashboard), "--brand-profile", str(profile),
                "--peer-html", str(presentation), "--json",
            ], capture_output=True, text=True)
            payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertIn("BRAND_PEER_MISMATCH", {item["code"] for item in payload["findings"]})

    def test_unreachable_source_blocks_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "blocked.json"
            result = subprocess.run([
                "python3", str(RESOLVER), "--url", "http://127.0.0.1:9/unreachable",
                "--output", str(output), "--id", "blocked-brand",
            ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("BLOCKED", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
