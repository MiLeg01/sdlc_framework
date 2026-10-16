#!/usr/bin/env python3
"""Validate static HTML, brand-profile consistency, and independent brand fidelity."""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


# Widest viewport still treated as a mobile reflow state by capture_brand_qa.mjs.
MOBILE_WIDTH = 480


class Inspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[str] = []
        self.ids: list[str] = []
        self.external: list[str] = []
        self.buttons: list[dict[str, str | None]] = []
        self.icons: list[dict[str, str]] = []
        self.brand_logos: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)
        values = {key: value or "" for key, value in attrs}
        if values.get("id"):
            self.ids.append(values["id"])
        if tag in {"script", "link", "img", "iframe", "video", "audio", "source"}:
            target = values.get("src") or values.get("href")
            if target and urlparse(target).scheme in {"http", "https"}:
                self.external.append(target)
        if tag == "button":
            self.buttons.append({"aria-label": values.get("aria-label"), "title": values.get("title")})
        if tag == "link" and "icon" in values.get("rel", "").lower().split():
            self.icons.append(values)
        if tag == "img" and ("data-brand-logo" in values or values.get("data-brand-asset") == "logo"):
            self.brand_logos.append(values)


def add(findings: list[dict[str, str]], code: str, detail: str, severity: str = "error") -> None:
    findings.append({"severity": severity, "code": code, "detail": detail})


def embedded_bytes(data_uri: str) -> bytes:
    if not data_uri.startswith("data:") or "," not in data_uri or ";base64" not in data_uri.split(",", 1)[0]:
        raise ValueError("asset is not a base64 data URI")
    try:
        decoded = base64.b64decode(data_uri.split(",", 1)[1], validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ValueError("asset data URI is invalid") from exc
    if not decoded:
        raise ValueError("asset data URI is empty")
    return decoded


def rgb_to_hex(value: str) -> str | None:
    match = re.fullmatch(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*([\d.]+))?\s*\)", value.lower())
    if not match:
        return value.lower() if re.fullmatch(r"#[0-9a-f]{6}", value.lower()) else None
    red, green, blue, alpha = match.groups()
    if alpha is not None and float(alpha) == 0:
        return None
    return "#" + "".join(f"{min(255, int(channel)):02x}" for channel in (red, green, blue))


def validate_qa_manifest(path: Path, profile: dict[str, object], html_path: Path, findings: list[dict[str, str]]) -> bool:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        add(findings, "BRAND_VISUAL_QA_INVALID", str(exc))
        return False
    for field in ("profile_fingerprint", "theme_fingerprint", "asset_fingerprint"):
        if manifest.get(field) != profile.get(field):
            add(findings, "BRAND_VISUAL_QA_STALE", f"{field} differs")
    if manifest.get("html_sha256") != hashlib.sha256(html_path.read_bytes()).hexdigest():
        add(findings, "BRAND_VISUAL_QA_STALE", "HTML fingerprint differs")
    for role in ("favicon", "logo"):
        if manifest.get("assets", {}).get(role) != profile["assets"][role]["sha256"]:
            add(findings, "BRAND_VISUAL_QA_ASSET_MISMATCH", role)
    required_roles = {
        "dashboard": {"body", "header", "navigation", "link", "button", "focus", "status", "panel", "table", "footer"},
        "presentation": {"body", "header", "navigation", "link", "button", "focus", "panel", "footer"},
    }
    artifact_kind = manifest.get("artifact_kind")
    roles = required_roles.get(artifact_kind)
    if not roles:
        add(findings, "BRAND_VISUAL_QA_INVALID", "artifact_kind must be dashboard or presentation")
        roles = set()
    elements = manifest.get("elements")
    if not isinstance(elements, list):
        add(findings, "BRAND_VISUAL_QA_INVALID", "elements must be an array")
        elements = []
    by_role = {item.get("role"): item for item in elements if isinstance(item, dict)}
    for role in sorted(roles):
        item = by_role.get(role)
        if not item or item.get("visible") is not True or not isinstance(item.get("styles"), dict):
            add(findings, "BRAND_COMPUTED_STYLE_MISSING", role)
    brand_scripts = Path(__file__).resolve().parents[2] / "build-living-dashboard" / "scripts"
    sys.path.insert(0, str(brand_scripts))
    from brand_profile import GENERIC_VISIBLE_COLORS
    allowed_colors = set(profile["theme"]["colors"].values()) | {item["value"] for item in profile.get("derived_tokens", [])}
    for item in by_role.values():
        for property_name, value in item.get("styles", {}).items():
            color = rgb_to_hex(str(value))
            if color in GENERIC_VISIBLE_COLORS and color not in set(profile["theme"]["colors"].values()):
                add(findings, "BRAND_GENERIC_PALETTE_RESIDUAL", f"{item.get('role')}.{property_name}={color}")
            elif color and color not in allowed_colors:
                add(findings, "BRAND_UNPROVEN_COMPUTED_COLOR", f"{item.get('role')}.{property_name}={color}")
    browser = manifest.get("browser")
    if not isinstance(browser, dict) or browser.get("engine") != "chromium":
        add(findings, "BRAND_VISUAL_QA_INVALID", "Chromium browser evidence is required")
    elif browser.get("console_errors"):
        add(findings, "BRAND_BROWSER_CONSOLE_ERROR", json.dumps(browser.get("console_errors"), ensure_ascii=False))
    responsive = manifest.get("responsive")
    if not isinstance(responsive, list) or not responsive:
        add(findings, "BRAND_RESPONSIVE_EVIDENCE_MISSING", "per-viewport brand evidence is required")
        responsive = []
    states = [item for item in responsive if isinstance(item, dict) and isinstance(item.get("viewport"), list)]
    if responsive and not any(state["viewport"][0] <= MOBILE_WIDTH for state in states):
        add(
            findings,
            "BRAND_RESPONSIVE_EVIDENCE_MISSING",
            f"no captured viewport is {MOBILE_WIDTH}px or narrower",
        )
    for state in states:
        label = f"{state.get('id', 'unnamed')}@{state['viewport'][0]}"
        if state.get("horizontal_overflow") is True:
            sources = ", ".join(str(item.get("element")) for item in state.get("overflow_sources", [])[:3])
            add(
                findings,
                "BRAND_RESPONSIVE_OVERFLOW",
                f"{label}: document {state.get('document_width')}px exceeds viewport "
                f"{state.get('viewport_width')}px{f' ({sources})' if sources else ''}",
            )
        if state.get("brand_visible") is not True:
            add(findings, "BRAND_NOT_VISIBLY_EXPRESSED", f"{label}: official identity is not visible")
    render = manifest.get("browser_render")
    if not isinstance(render, dict) or render.get("brand_visible") is not True:
        add(findings, "BRAND_NOT_VISIBLY_EXPRESSED", "browser render did not confirm visible official identity")
    screenshot = render.get("screenshot") if isinstance(render, dict) else None
    if not isinstance(screenshot, str) or not screenshot or not (path.parent / screenshot).is_file():
        add(findings, "BRAND_VISUAL_QA_SCREENSHOT_MISSING", str(screenshot or ""))
    return not any(item["severity"] == "error" and item["code"].startswith("BRAND_") for item in findings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--allow-external", action="store_true")
    parser.add_argument("--brand-profile", type=Path)
    parser.add_argument("--brand-qa", type=Path)
    parser.add_argument("--peer-html", type=Path)
    args = parser.parse_args()
    text = args.html.read_text(encoding="utf-8")
    inspector = Inspector()
    inspector.feed(text)
    findings: list[dict[str, str]] = []

    for tag in ["html", "head", "body", "title"]:
        if tag not in inspector.tags:
            add(findings, "MISSING_TAG", tag)
    duplicates = sorted({value for value in inspector.ids if inspector.ids.count(value) > 1})
    for value in duplicates:
        add(findings, "DUPLICATE_ID", value)
    if inspector.external and not args.allow_external:
        for target in inspector.external:
            add(findings, "EXTERNAL_DEPENDENCY", target)
    if "prefers-reduced-motion" not in text:
        add(findings, "NO_REDUCED_MOTION", "missing reduced-motion CSS", "warning")
    if not re.search(r"@media\s+print", text, re.I):
        add(findings, "NO_PRINT_STYLE", "missing print CSS", "warning")
    if not re.search(r":focus-visible|:focus\b", text, re.I):
        add(findings, "NO_FOCUS_STYLE", "no explicit focus style", "warning")
    if "<main" not in text.lower():
        add(findings, "NO_MAIN_LANDMARK", "missing main landmark", "warning")
    if re.search(r"<img\b(?![^>]*\balt=)", text, re.I):
        add(findings, "IMAGE_WITHOUT_ALT", "at least one image lacks alt")
    if re.search(r"<button\b[^>]*>\s*(?:<[^>]+>\s*)*</button>", text, re.I):
        add(findings, "EMPTY_BUTTON", "empty button requires an accessible name", "warning")

    static_errors = sum(item["severity"] == "error" for item in findings)
    profile_consistent: bool | None = None
    brand_fidelity: bool | None = None
    visual_qa: bool | None = None
    profile = None

    if args.brand_profile:
        brand_scripts = Path(__file__).resolve().parents[2] / "build-living-dashboard" / "scripts"
        sys.path.insert(0, str(brand_scripts))
        try:
            from brand_profile import GENERIC_VISIBLE_COLORS, css_variables, validate_brand_profile
            profile = validate_brand_profile(json.loads(args.brand_profile.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            add(findings, "BRAND_PROFILE_INVALID", str(exc))
            profile_consistent = False
            brand_fidelity = False
            visual_qa = False
        else:
            brand_start = len(findings)
            expected_markers = {
                "data-brand-id": str(profile["id"]),
                "data-brand-status": str(profile["status"]),
                "data-brand-profile-fingerprint": str(profile["profile_fingerprint"]),
                "data-brand-theme-fingerprint": str(profile["theme_fingerprint"]),
                "data-brand-asset-fingerprint": str(profile["asset_fingerprint"]),
            }
            for attribute, value in expected_markers.items():
                if not re.search(rf'{re.escape(attribute)}=["\']{re.escape(value)}["\']', text):
                    add(findings, "BRAND_MARKER_MISSING", f"{attribute}={value}")
            for variable, expected in css_variables(profile).items():
                if not re.search(rf'{re.escape(variable)}\s*:\s*{re.escape(expected)}(?:\s*[;}}])', text, re.I):
                    add(findings, "BRAND_TOKEN_MISMATCH", f"{variable} expected {expected}")
            for field in ("profile_fingerprint", "theme_fingerprint", "asset_fingerprint"):
                if str(profile[field]) not in text:
                    add(findings, "BRAND_PROFILE_NOT_EMBEDDED", f"missing {field}")

            expected_favicon = profile["assets"]["favicon"]
            matching_icon = next((item for item in inspector.icons if item.get("data-brand-asset") == "favicon"), None)
            try:
                icon_bytes = embedded_bytes(matching_icon.get("href", "") if matching_icon else "")
            except ValueError as exc:
                add(findings, "BRAND_FAVICON_MISMATCH", str(exc))
            else:
                if hashlib.sha256(icon_bytes).hexdigest() != expected_favicon["sha256"]:
                    add(findings, "BRAND_FAVICON_MISMATCH", "rendered favicon bytes differ from selected official favicon")

            expected_logo = profile["assets"]["logo"]
            if not inspector.brand_logos or re.search(r'<[^>]*class=["\'][^"\']*brand-mark[^"\']*["\'][^>]*>\s*(?:AC|project|[A-Z]{1,3})\s*<', text, re.I):
                add(findings, "BRAND_LOGO_PLACEHOLDER", "official logo resolved but placeholder identity is rendered")
            else:
                try:
                    logo_bytes = embedded_bytes(inspector.brand_logos[0].get("src", ""))
                except ValueError as exc:
                    add(findings, "BRAND_LOGO_MISMATCH", str(exc))
                else:
                    if hashlib.sha256(logo_bytes).hexdigest() != expected_logo["sha256"]:
                        add(findings, "BRAND_LOGO_MISMATCH", "rendered logo bytes differ from selected official logo")

            scan_text = re.sub(r":root\s*\{[^}]*\}", "", text, count=1, flags=re.S)
            scan_text = re.sub(r"/\* BRAND_PROFILE_START \*/.*?/\* BRAND_PROFILE_END \*/", "", scan_text, flags=re.S)
            observed_or_derived = set(profile["theme"]["colors"].values()) | {item["value"] for item in profile.get("derived_tokens", [])}
            for color in sorted({value.lower() for value in re.findall(r"#[0-9a-fA-F]{6}\b", scan_text)}):
                if color in GENERIC_VISIBLE_COLORS and color not in observed_or_derived:
                    add(findings, "BRAND_GENERIC_PALETTE_RESIDUAL", color)

            profile_consistent = not any(item["severity"] == "error" for item in findings[brand_start:])
            if args.peer_html:
                peer = args.peer_html.read_text(encoding="utf-8")
                for marker in expected_markers.values():
                    if marker not in peer:
                        add(findings, "BRAND_PEER_MISMATCH", f"peer artifact lacks {marker}")
                for role in ("favicon", "logo"):
                    if profile["assets"][role]["data_uri"] not in peer:
                        add(findings, "BRAND_PEER_MISMATCH", f"peer artifact differs for {role}")
                profile_consistent = profile_consistent and not any(item["code"] == "BRAND_PEER_MISMATCH" for item in findings)
            if args.brand_qa:
                visual_qa = validate_qa_manifest(args.brand_qa, profile, args.html, findings)
            else:
                visual_qa = False
                add(findings, "BRAND_VISUAL_QA_MISSING", "browser computed-style and visible-brand evidence is required")
            brand_fidelity = bool(profile_consistent and visual_qa and not any(
                item["severity"] == "error" and item["code"] in {
                    "BRAND_FAVICON_MISMATCH", "BRAND_LOGO_PLACEHOLDER", "BRAND_LOGO_MISMATCH",
                    "BRAND_GENERIC_PALETTE_RESIDUAL", "BRAND_PEER_MISMATCH", "BRAND_NOT_VISIBLY_EXPRESSED",
                } for item in findings
            ))

    errors = sum(item["severity"] == "error" for item in findings)
    checks = {
        "STRUCTURE_PASS": None,
        "STATIC_HTML_PASS": static_errors == 0,
        "BRAND_PROFILE_CONSISTENT": profile_consistent,
        "BRAND_FIDELITY_PASS": brand_fidelity,
        "VISUAL_QA_PASS": visual_qa,
    }
    result = {
        "file": str(args.html), "status": "PASS" if errors == 0 else "FAIL", "errors": errors,
        "warnings": sum(item["severity"] == "warning" for item in findings), "checks": checks, "findings": findings,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['status']}: {args.html} ({result['errors']} errors, {result['warnings']} warnings)")
        for name, value in checks.items():
            print(f"{name}: {'NOT_RUN' if value is None else ('PASS' if value else 'FAIL')}")
        for item in findings:
            print(f"{item['severity'].upper()} {item['code']}: {item['detail']}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
