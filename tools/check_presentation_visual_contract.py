#!/usr/bin/env python3
"""Reject visual or interaction drift in the locked Agent Commons presentation."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
PRESENTATION_PATH = ROOT / "presentation" / "index.html"
CONTRACT_PATH = ROOT / "presentation" / "visual-contract.json"

CONTENT_ATTRIBUTES = {
    "alt",
    "aria-description",
    "aria-label",
    "content",
    "placeholder",
    "title",
    "value",
}


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class StructureParser(HTMLParser):
    """Capture markup and visual attributes while intentionally ignoring text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tokens: list[str] = []
        self.data_theme = ""
        self.data_visual_thesis = ""
        self.theme_color = ""

    def handle_decl(self, decl: str) -> None:
        self.tokens.append(f"<!{decl.lower()}>")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.data_theme = values.get("data-theme", "") or ""
            self.data_visual_thesis = values.get("data-visual-thesis", "") or ""
        if tag == "meta" and values.get("name", "").lower() == "theme-color":
            self.theme_color = values.get("content", "") or ""
        locked_attrs = sorted(
            (name, value or "")
            for name, value in attrs
            if name not in CONTENT_ATTRIBUTES
        )
        self.tokens.append(f"<{tag}{json.dumps(locked_attrs, separators=(',', ':'))}>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.tokens.append(f"</{tag}>")

    def handle_endtag(self, tag: str) -> None:
        self.tokens.append(f"</{tag}>")


def extract_single(pattern: str, html: str, label: str) -> str:
    matches = re.findall(pattern, html, flags=re.IGNORECASE | re.DOTALL)
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {label}, found {len(matches)}")
    return matches[0]


def observed_contract(html: str) -> dict[str, str]:
    parser = StructureParser()
    parser.feed(html)
    parser.close()
    style = extract_single(r"<style\b[^>]*>(.*?)</style>", html, "style block")
    inline_scripts = re.findall(
        r"<script\b(?![^>]*\bsrc\s*=)[^>]*>(.*?)</script>",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return {
        "data_theme": parser.data_theme,
        "data_visual_thesis": parser.data_visual_thesis,
        "theme_color": parser.theme_color,
        "style_sha256": digest(style),
        "structure_sha256": digest("\n".join(parser.tokens)),
        "behavior_sha256": digest("\n".join(inline_scripts)),
    }


def validate(html: str, contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = contract.get("locked")
    if not isinstance(expected, dict):
        return ["visual-contract.json must contain a locked object"]
    try:
        observed = observed_contract(html)
    except ValueError as exc:
        return [str(exc)]
    for key, expected_value in expected.items():
        if observed.get(key) != expected_value:
            errors.append(f"{key} drifted from the locked visual system")
    for key in observed.keys() - expected.keys():
        errors.append(f"visual contract does not lock {key}")
    return errors


def validate_current() -> list[str]:
    try:
        html = PRESENTATION_PATH.read_text(encoding="utf-8")
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [str(exc)]
    return validate(html, contract)


def main() -> int:
    errors = validate_current()
    if errors:
        print("Presentation visual contract: FAIL")
        for error in errors:
            print(f"ERROR {error}")
        return 1
    print("Presentation visual contract: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
