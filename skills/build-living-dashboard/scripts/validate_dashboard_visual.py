#!/usr/bin/env python3
"""Validate canonical dashboard design grammar and rendered visual-QA evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


ASSET_ROOT = Path(__file__).resolve().parent.parent / "assets"
CONTRACT_PATH = ASSET_ROOT / "dashboard-visual-contract.json"
SHELL_PATH = ASSET_ROOT / "dashboard-shell.html"
BRAND_START = "/* BRAND_PROFILE_START */"
BRAND_END = "/* BRAND_PROFILE_END */"


class DashboardVisualError(ValueError):
    """The dashboard has drifted from the canonical visual product contract."""


class DashboardParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_attributes: dict[str, str] = {}
        self.style_parts: list[str] = []
        self.data_parts: list[str] = []
        self._style = False
        self._data = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.html_attributes = attributes
        if tag == "style":
            self._style = True
        if tag == "script" and attributes.get("id") == "dashboard-data":
            self._data = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "style":
            self._style = False
        if tag == "script" and self._data:
            self._data = False

    def handle_data(self, data: str) -> None:
        if self._style:
            self.style_parts.append(data)
        if self._data:
            self.data_parts.append(data)


def load_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract.get("schema_version") != 1 or not contract.get("required_rendered_states"):
        raise DashboardVisualError("canonical dashboard visual contract is invalid")
    return contract


def contract_fingerprint(contract: dict[str, Any] | None = None) -> str:
    contract = contract or load_contract()
    canonical = json.dumps(contract, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _style_without_brand(style: str) -> str:
    if BRAND_START not in style or BRAND_END not in style:
        raise DashboardVisualError("brand style boundary markers are missing")
    start = style.index(BRAND_START) + len(BRAND_START)
    end = style.index(BRAND_END, start)
    return style[:start] + style[end:]


def template_style_fingerprint() -> str:
    shell = SHELL_PATH.read_text(encoding="utf-8")
    matches = re.findall(r"<style>(.*?)</style>", shell, re.DOTALL)
    if not matches:
        raise DashboardVisualError("canonical dashboard shell has no style block")
    normalized = _style_without_brand("\n".join(matches)).replace("__BRAND_STYLE__", "")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def resolved_design_fingerprint() -> str:
    return hashlib.sha256(f"{contract_fingerprint()}:{template_style_fingerprint()}".encode("utf-8")).hexdigest()


def _parse(html_path: Path) -> tuple[DashboardParser, dict[str, Any], str]:
    parser = DashboardParser()
    parser.feed(html_path.read_text(encoding="utf-8"))
    try:
        data = json.loads("".join(parser.data_parts))
    except json.JSONDecodeError as exc:
        raise DashboardVisualError(f"embedded dashboard data is invalid: {exc}") from exc
    return parser, data, "".join(parser.style_parts)


def _validate_static(parser: DashboardParser, data: dict[str, Any], style: str, contract: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    expected_contract = contract_fingerprint(contract)
    expected_design = resolved_design_fingerprint()
    visual = data.get("dashboard_visual_contract")
    if not isinstance(visual, dict):
        failures.append("dashboard_visual_contract is missing from canonical dashboard data")
    else:
        if visual.get("id") != contract["id"]:
            failures.append("dashboard visual contract ID differs")
        if visual.get("contract_fingerprint") != expected_contract:
            failures.append("dashboard visual contract fingerprint differs")
        if visual.get("design_fingerprint") != expected_design:
            failures.append("dashboard design fingerprint differs")
    if parser.html_attributes.get("data-dashboard-design-id") != contract["id"]:
        failures.append("rendered dashboard design ID differs")
    if parser.html_attributes.get("data-dashboard-design-fingerprint") != expected_design:
        failures.append("rendered dashboard design fingerprint differs")
    try:
        normalized_style = _style_without_brand(style)
    except DashboardVisualError as exc:
        failures.append(str(exc))
        normalized_style = style
    for fragment in contract["required_css_fragments"]:
        if fragment not in normalized_style:
            failures.append(f"required visual grammar fragment is missing: {fragment}")
    lowered = normalized_style.casefold()
    for pattern in contract["forbidden_css_patterns"]:
        if pattern.casefold() in lowered:
            failures.append(f"forbidden visual drift pattern is present: {pattern}")
    root_match = re.search(r":root\{([^}]*)\}", normalized_style)
    if not root_match:
        failures.append("canonical root design tokens are missing")
    else:
        for token in contract.get("required_tokens", []):
            if f"{token}:" not in root_match.group(1):
                failures.append(f"required visual token is missing: {token}")
        radius_match = re.search(r"--radius:([0-9.]+)px", root_match.group(1))
        if not radius_match:
            failures.append("default radius token is missing or not expressed in pixels")
        elif float(radius_match.group(1)) > float(contract["anti_drift"]["maximum_default_radius_px"]):
            failures.append("default radius exceeds the canonical editorial maximum")
    pill_rules = re.findall(r"([^{}]+)\{[^{}]*border-radius:999px[^{}]*\}", normalized_style)
    allowed = set(contract["anti_drift"]["allowed_pill_selectors"])
    for selector_group in pill_rules:
        for selector in (item.strip() for item in selector_group.split(",")):
            if selector not in allowed:
                failures.append(f"unsupported pill styling: {selector}")
    return failures


def _validate_qa_manifest(
    manifest_path: Path,
    html_path: Path,
    data: dict[str, Any],
    contract: dict[str, Any],
) -> list[str]:
    failures: list[str] = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot load visual QA manifest: {exc}"]
    if manifest.get("schema_version") != 2:
        failures.append("visual QA manifest schema_version must be 2")
    fingerprints = manifest.get("fingerprints")
    if not isinstance(fingerprints, dict):
        fingerprints = {}
        failures.append("visual QA manifest fingerprints must be an object")
    if fingerprints.get("design") != resolved_design_fingerprint():
        failures.append("visual QA manifest design fingerprint is stale")
    states = manifest.get("states")
    if not isinstance(states, list):
        return failures + ["visual QA manifest states must be an array"]
    by_id = {item.get("id"): item for item in states if isinstance(item, dict)}
    for required in contract["required_rendered_states"]:
        result = by_id.get(required["id"])
        if not result:
            failures.append(f"required rendered state is missing: {required['id']}")
            continue
        if result.get("status") != "PASS":
            failures.append(f"rendered state did not pass: {required['id']}")
        if result.get("viewport") != required["viewport"]:
            failures.append(f"rendered state viewport differs: {required['id']}")
        screenshot = result.get("screenshot")
        if not isinstance(screenshot, str) or not screenshot:
            failures.append(f"rendered state screenshot is missing: {required['id']}")
        else:
            candidate = (manifest_path.parent / screenshot).resolve()
            if not candidate.is_file():
                failures.append(f"rendered state screenshot does not exist: {required['id']} -> {candidate}")
        if required.get("locale") and result.get("locale") != required["locale"]:
            failures.append(f"rendered state locale differs: {required['id']}")
    if fingerprints.get("html") != hashlib.sha256(html_path.read_bytes()).hexdigest():
        failures.append("visual QA manifest HTML fingerprint is stale")
    if fingerprints.get("data") != data.get("fingerprint"):
        failures.append("visual QA manifest data fingerprint is stale")
    profile = data.get("brand_profile")
    if profile and profile.get("required"):
        brand = manifest.get("brand")
        if not isinstance(brand, dict) or brand.get("status") != "PASS":
            failures.append("required client-brand visual QA did not pass")
        else:
            for field in ("profile_fingerprint", "theme_fingerprint", "asset_fingerprint"):
                if brand.get(field) != profile.get(field) or fingerprints.get(f"brand_{field.removesuffix('_fingerprint')}") != profile.get(field):
                    failures.append(f"client-brand visual QA {field} differs")
            visible_roles = brand.get("visible_roles")
            if not isinstance(visible_roles, dict):
                failures.append("client-brand visual QA visible semantic roles are missing")
            else:
                for role, expected in profile.get("semantic_roles", {}).items():
                    observed = visible_roles.get(role)
                    if role == "identity":
                        if not isinstance(observed, dict) or observed.get("asset_fingerprint") != expected.get("asset_fingerprint") or observed.get("visible") is not True:
                            failures.append("client-brand identity role is not visibly evidenced")
                    elif not isinstance(observed, dict) or observed.get("value") != expected.get("value") or observed.get("visible") is not True:
                        failures.append(f"client-brand semantic role is not visibly evidenced: {role}")
    results = manifest.get("results")
    if not isinstance(results, dict):
        return failures + ["visual QA manifest results must be an object"]
    required_results = {"STRUCTURE_PASS", "STATIC_HTML_PASS", "VISUAL_QA_PASS", "ACCESSIBILITY_PASS"}
    if profile and profile.get("required"):
        required_results.update({"BRAND_PROFILE_CONSISTENT", "BRAND_FIDELITY_PASS"})
    languages = data.get("delivery", {}).get("languages", ["en"])
    if len(languages) > 1:
        required_results.add("LOCALIZATION_PASS")
    for name in sorted(required_results):
        result = results.get(name)
        if not isinstance(result, dict) or result.get("status") != "PASS":
            failures.append(f"required lifecycle QA result did not pass: {name}")
            continue
        if not isinstance(result.get("producer"), str) or not result["producer"].strip():
            failures.append(f"required lifecycle QA result has no independent producer: {name}")
        if name == "LOCALIZATION_PASS":
            locales = result.get("locales")
            if not isinstance(locales, dict) or any(locales.get(locale) != "PASS" for locale in languages):
                failures.append("localization QA does not pass every configured language")
    return failures


def validate(html_path: Path, qa_manifest: Path | None = None, require_qa: bool = False) -> dict[str, Any]:
    contract = load_contract()
    parser, data, style = _parse(html_path)
    static_failures = _validate_static(parser, data, style, contract)
    failures = list(static_failures)
    qa_failures: list[str] = []
    if qa_manifest:
        qa_failures = _validate_qa_manifest(qa_manifest, html_path, data, contract)
        failures.extend(qa_failures)
    elif require_qa:
        qa_failures.append("rendered visual QA manifest is required")
        failures.extend(qa_failures)
    profile = data.get("brand_profile") if isinstance(data.get("brand_profile"), dict) else None
    brand_consistent = None
    brand_fidelity = None
    if profile:
        brand_consistent = parser.html_attributes.get("data-brand-profile-fingerprint") == profile.get("profile_fingerprint")
        brand_fidelity = bool(brand_consistent and qa_manifest is not None and not any("brand" in failure.lower() for failure in qa_failures))
    lifecycle_status = "VALIDATED" if qa_manifest is not None and not failures else ("BLOCKED" if require_qa or failures else "PARTIAL")
    return {
        "status": "FAIL" if failures else "PASS",
        "lifecycle_status": lifecycle_status,
        "html": str(html_path),
        "contract_id": contract["id"],
        "contract_fingerprint": contract_fingerprint(contract),
        "design_fingerprint": resolved_design_fingerprint(),
        "qa_manifest": str(qa_manifest) if qa_manifest else None,
        "fingerprints": {
            "html": hashlib.sha256(html_path.read_bytes()).hexdigest(),
            "design": resolved_design_fingerprint(),
            "data": data.get("fingerprint"),
            "brand_profile": profile.get("profile_fingerprint") if profile else None,
            "brand_theme": profile.get("theme_fingerprint") if profile else None,
            "brand_asset": profile.get("asset_fingerprint") if profile else None,
        },
        "checks": {
            "STRUCTURE_PASS": None,
            "STATIC_HTML_PASS": not static_failures,
            "BRAND_PROFILE_CONSISTENT": brand_consistent,
            "BRAND_FIDELITY_PASS": brand_fidelity,
            "VISUAL_QA_PASS": not qa_failures if qa_manifest or require_qa else None,
            "ACCESSIBILITY_PASS": None if not qa_manifest else not any("ACCESSIBILITY_PASS" in failure for failure in qa_failures),
            "LOCALIZATION_PASS": None if not qa_manifest else not any("localization" in failure.lower() for failure in qa_failures),
        },
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--qa-manifest", type=Path)
    parser.add_argument("--require-qa", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate(args.html, args.qa_manifest, args.require_qa)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["status"] == "PASS":
        for name, value in result["checks"].items():
            print(f"{name}: {'NOT_RUN' if value is None else ('PASS' if value else 'FAIL')}")
        print("Dashboard visual fidelity: PASS")
    else:
        print("Dashboard visual fidelity: FAIL")
        for failure in result["failures"]:
            print(f"- {failure}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
