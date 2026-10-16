#!/usr/bin/env python3
"""Validate semantic completeness of a resolved canonical living-dashboard state."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import sys


STRUCTURE_PATH = Path(__file__).resolve().parent.parent / "assets" / "dashboard-structure.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_dashboard import semantic_content_failures


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hidden_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "template"}:
            self.hidden_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "template"} and self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.hidden_depth and data.strip():
            self.parts.append(data.strip())

    def text(self) -> str:
        return " ".join(" ".join(self.parts).split())


def validate(data: dict, peer_html: str | None = None) -> list[str]:
    failures: list[str] = []
    structure = json.loads(STRUCTURE_PATH.read_text(encoding="utf-8"))
    expected = structure["information_domains"]
    resolved_structure = data.get("dashboard_structure")
    if not isinstance(resolved_structure, dict):
        return ["dashboard_structure is missing"]
    domains = resolved_structure.get("information_domains")
    if not isinstance(domains, list):
        return ["dashboard_structure.information_domains is missing"]
    expected_ids = [item["id"] for item in expected]
    actual_ids = [item.get("id") for item in domains if isinstance(item, dict)]
    missing = [identifier for identifier in expected_ids if identifier not in actual_ids]
    extra = [identifier for identifier in actual_ids if identifier not in expected_ids]
    duplicates = sorted(identifier for identifier, count in Counter(actual_ids).items() if count > 1)
    if missing:
        failures.append(f"missing information domains: {', '.join(missing)}")
    if extra:
        failures.append(f"unknown information domains: {', '.join(str(value) for value in extra)}")
    if duplicates:
        failures.append(f"duplicate information domains: {', '.join(str(value) for value in duplicates)}")
    if actual_ids != expected_ids:
        failures.append("information-domain order differs from the canonical contract")
    allowed_states = set(structure["domain_states"])
    expected_sections = {item["id"]: item["section_id"] for item in expected}
    for domain in domains:
        if not isinstance(domain, dict):
            failures.append("information-domain entries must be objects")
            continue
        identifier = domain.get("id")
        if domain.get("status") not in allowed_states:
            failures.append(f"{identifier}: invalid or missing state")
        if not str(domain.get("reason", "")).strip():
            failures.append(f"{identifier}: state reason is missing")
        if identifier in expected_sections and domain.get("section_id") != expected_sections[identifier]:
            failures.append(f"{identifier}: canonical section mapping differs")
        if domain.get("basis") not in {"MEASURED", "ASSESSED", "MIXED", "UNKNOWN", "NOT_APPLICABLE"}:
            failures.append(f"{identifier}: measured/assessed basis is missing or invalid")
    profile = data.get("dashboard", {}).get("profile") if isinstance(data.get("dashboard"), dict) else None
    if profile == "legacy-modernization":
        required = {
            "management-overview", "system-statistics", "complexity", "estimation", "roadmap",
            "inventory", "system-landscape", "component-architecture", "data-persistence",
            "integrations", "requirements", "openspec-specifications", "legacy-test-quality",
            "risks-decisions", "open-questions", "evidence",
        }
        absent = sorted(required - set(actual_ids))
        if absent:
            failures.append(f"legacy-modernization semantic domains absent: {', '.join(absent)}")
    failures.extend(semantic_content_failures(data))
    claims = data.get("dashboard", {}).get("shared_claims", []) if isinstance(data.get("dashboard"), dict) else []
    if claims:
        if peer_html is None:
            failures.append("dashboard.shared_claims require --peer-html for parity validation")
        else:
            parser = VisibleTextParser()
            parser.feed(peer_html)
            visible = parser.text()
            for claim in claims:
                identifier = claim.get("id", "<unknown>") if isinstance(claim, dict) else "<invalid>"
                for marker in claim.get("peer_markers", []) if isinstance(claim, dict) else []:
                    if marker not in visible:
                        failures.append(f"shared claim {identifier}: peer marker missing: {marker}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--peer-html", type=Path)
    args = parser.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    peer_html = args.peer_html.read_text(encoding="utf-8") if args.peer_html else None
    failures = validate(data, peer_html)
    if failures:
        print("SEMANTIC_FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("SEMANTIC_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
