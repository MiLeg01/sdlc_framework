#!/usr/bin/env python3
"""Validate a generated dashboard against the canonical structural contract."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re


STRUCTURE_PATH = Path(__file__).resolve().parent.parent / "assets" / "dashboard-structure.json"


class DashboardParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.sections: list[str] = []
        self.nav_targets: list[str] = []
        self.global_hooks: set[str] = set()
        self.section_hooks: dict[str, set[str]] = defaultdict(set)
        self.section_regions: dict[str, set[str]] = defaultdict(set)
        self.information_domains: list[tuple[str, str]] = []
        self.current_section: str | None = None
        self.data_script = False
        self.data_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        identifier = values.get("id")
        if identifier:
            self.ids.append(identifier)
        if tag == "section" and "data-canonical-section" in values:
            self.current_section = values["data-canonical-section"]
            self.sections.append(self.current_section)
        if "data-section-target" in values:
            self.nav_targets.append(values["data-section-target"])
        hook = values.get("data-dashboard-hook")
        if hook:
            self.global_hooks.add(hook)
            if self.current_section:
                self.section_hooks[self.current_section].add(hook)
        region = values.get("data-dashboard-region")
        if region and self.current_section:
            self.section_regions[self.current_section].add(region)
        domain = values.get("data-information-domain")
        if domain:
            self.information_domains.append((domain, self.current_section or ""))
        if tag == "script" and identifier == "dashboard-data":
            self.data_script = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "section":
            self.current_section = None
        if tag == "script" and self.data_script:
            self.data_script = False

    def handle_data(self, data: str) -> None:
        if self.data_script:
            self.data_parts.append(data)


def load_expected(parser: DashboardParser, data_path: Path | None) -> dict:
    if data_path:
        data = json.loads(data_path.read_text(encoding="utf-8"))
    else:
        payload = "".join(parser.data_parts).strip()
        if not payload:
            raise ValueError("dashboard-data JSON is missing; pass --data for an external canonical export")
        data = json.loads(payload)
    structure = data.get("dashboard_structure")
    if not isinstance(structure, dict) or not structure.get("sections"):
        raise ValueError("dashboard_structure is missing from canonical dashboard data")
    return structure


def validate_canonical_contract(expected: dict) -> list[str]:
    canonical = json.loads(STRUCTURE_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []
    serialized = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    fingerprint = hashlib.sha256(serialized.encode()).hexdigest()
    if expected.get("id") != canonical["id"]:
        failures.append(f"structure ID differs: expected {canonical['id']}, found {expected.get('id')}")
    if expected.get("fingerprint") != fingerprint:
        failures.append("canonical structure fingerprint differs")
    if expected.get("navigation_model") != canonical["navigation"]["model"]:
        failures.append("desktop navigation model differs")
    if expected.get("mobile_navigation_model") != canonical["navigation"]["mobile_model"]:
        failures.append("mobile navigation model differs")
    if expected.get("chrome") != canonical.get("chrome"):
        failures.append("dashboard chrome contract differs")

    canonical_sections = {item["id"]: item for item in canonical["sections"]}
    extension_points = {item["id"]: item for item in canonical["extension_points"]}
    sections = expected.get("sections", [])
    section_ids = [item.get("id") for item in sections]
    duplicates = sorted(identifier for identifier, count in Counter(section_ids).items()
                        if identifier and count > 1)
    if duplicates:
        failures.append(f"duplicate resolved section IDs: {', '.join(duplicates)}")
    core_ids = [item["id"] for item in canonical["sections"] if item["classification"] == "core"]
    missing_core = [identifier for identifier in core_ids if identifier not in section_ids]
    if missing_core:
        failures.append(f"missing core sections: {', '.join(missing_core)}")
    if expected.get("mode") in {"canonical", "full-legacy-modernization"}:
        canonical_ids = [item["id"] for item in canonical["sections"]]
        if section_ids != canonical_ids:
            failures.append(
                "canonical dashboard sections differ from canonical order: "
                f"expected {canonical_ids}, found {section_ids}"
            )
    canonical_domains = canonical.get("information_domains", [])
    resolved_domains = expected.get("information_domains", [])
    if [item.get("id") for item in resolved_domains] != [item["id"] for item in canonical_domains]:
        failures.append("resolved information domains differ from canonical order")
    canonical_domain_map = {item["id"]: item["section_id"] for item in canonical_domains}
    for domain in resolved_domains:
        identifier = domain.get("id")
        if identifier not in canonical_domain_map:
            failures.append(f"unknown information domain: {identifier}")
        elif domain.get("section_id") != canonical_domain_map[identifier]:
            failures.append(f"{identifier} information-domain placement differs")
        if domain.get("status") not in canonical.get("domain_states", []):
            failures.append(f"{identifier} information-domain state is invalid")
    orders = [item.get("order") for item in sections]
    if any(not isinstance(order, int) for order in orders) or orders != sorted(orders):
        failures.append("resolved section order is outside the canonical order")

    for section in sections:
        identifier = section.get("id")
        if identifier in canonical_sections:
            source = canonical_sections[identifier]
            for field in ("classification", "group", "order"):
                if section.get(field) != source.get(field):
                    failures.append(f"{identifier} canonical {field} differs")
        elif section.get("classification") == "project-specific":
            point_id = section.get("extension_point")
            point = extension_points.get(point_id)
            if not point:
                failures.append(f"{identifier} uses an unsupported extension point: {point_id}")
                continue
            if section.get("group") != point["group"]:
                failures.append(f"{identifier} extension group differs from {point_id}")
            order = section.get("order")
            if not isinstance(order, int) or not point["order_min"] <= order <= point["order_max"]:
                failures.append(f"{identifier} is outside extension point {point_id}")
        else:
            failures.append(f"unknown non-extension section: {identifier}")

    groups = {item["id"]: item for item in canonical["navigation"]["groups"]}
    expected_navigation = expected.get("navigation", [])
    navigation_ids = [item.get("id") for item in expected_navigation]
    group_orders = [groups.get(identifier, {}).get("order", 999) for identifier in navigation_ids]
    if group_orders != sorted(group_orders):
        failures.append("navigation groups are outside canonical order")
    for navigation in expected_navigation:
        identifier = navigation.get("id")
        if identifier not in groups:
            failures.append(f"unknown navigation group: {identifier}")
            continue
        resolved_ids = [item["id"] for item in sections if item.get("group") == identifier]
        if navigation.get("section_ids") != resolved_ids:
            failures.append(f"navigation group {identifier} does not match resolved sections")
    groups_with_sections = [item["id"] for item in canonical["navigation"]["groups"]
                            if any(section.get("group") == item["id"] for section in sections)]
    if navigation_ids != groups_with_sections:
        failures.append("resolved navigation groups differ from canonical grouping")

    required_hooks = set(canonical["interaction_contract"]["required_hooks"])
    resolved_hooks = set(expected.get("interaction_contract", {}).get("required_hooks", []))
    if not required_hooks <= resolved_hooks:
        failures.append("canonical interaction contract hooks differ")
    return failures


def validate_html(path: Path, data_path: Path | None = None) -> list[str]:
    source = path.read_text(encoding="utf-8")
    parser = DashboardParser()
    parser.feed(source)
    expected = load_expected(parser, data_path)
    failures = validate_canonical_contract(expected)
    duplicates = sorted(identifier for identifier, count in Counter(parser.ids).items() if count > 1)
    if duplicates:
        failures.append(f"duplicate IDs: {', '.join(duplicates)}")
    expected_sections = [item["id"] for item in expected["sections"]]
    if parser.sections != expected_sections:
        failures.append(f"section order differs: expected {expected_sections}, found {parser.sections}")
    if parser.nav_targets != expected_sections:
        failures.append(f"navigation order differs: expected {expected_sections}, found {parser.nav_targets}")
    expected_domains = [
        (domain["id"], domain["section_id"])
        for section in expected["sections"]
        for domain in expected.get("information_domains", [])
        if domain["section_id"] == section["id"]
    ]
    if parser.information_domains != expected_domains:
        failures.append(f"information-domain slots differ: expected {expected_domains}, found {parser.information_domains}")
    for section in expected["sections"]:
        identifier = section["id"]
        missing_regions = sorted(set(section.get("required_regions", [])) - parser.section_regions[identifier])
        if missing_regions:
            failures.append(f"{identifier} missing regions: {', '.join(missing_regions)}")
        missing_hooks = sorted(set(section.get("required_hooks", [])) - parser.section_hooks[identifier])
        if missing_hooks:
            failures.append(f"{identifier} missing hooks: {', '.join(missing_hooks)}")
    required_global = set(expected.get("interaction_contract", {}).get("required_hooks", []))
    missing_global = sorted(required_global - parser.global_hooks)
    if missing_global:
        failures.append(f"missing global hooks: {', '.join(missing_global)}")
    if not re.search(r"@media\s*\(\s*max-width\s*:\s*720px\s*\)", source):
        failures.append("mobile breakpoint max-width:720px is missing")
    if "prefers-reduced-motion" not in source:
        failures.append("reduced-motion behavior is missing")
    for marker in (
        'id="data-integrity-state"', 'id="validation-state"', 'id="project-title"',
        'data-dashboard-hook="co-brand"', 'data-localization-switch',
        'id="generated-at"', 'id="canonical-state-fingerprint"', 'id="source-fingerprint"',
        'class="register-summary" role="status" aria-live="polite"', 'data-load-more=',
        'data-trace-depth',
    ):
        if marker not in source:
            failures.append(f"dashboard chrome marker is missing: {marker}")
    if re.search(r'id="validation-state"[^>]*dashboard\.status\.validated', source):
        failures.append("dashboard claims validation before lifecycle QA is complete")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--data", type=Path)
    args = parser.parse_args()
    try:
        failures = validate_html(args.html, args.data)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print("STRUCTURE_PASS: FAIL")
        print("Dashboard structure: FAIL")
        print(f"- {error}")
        return 1
    if failures:
        print("STRUCTURE_PASS: FAIL")
        print("Dashboard structure: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("STRUCTURE_PASS: PASS")
    print("Dashboard structure: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
