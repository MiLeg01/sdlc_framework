#!/usr/bin/env python3
"""Validate keyed client-artifact localization coverage, freshness, and preservation rules."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
NUMBER_RE = re.compile(r"(?<![A-Za-z0-9])[-+]?\d[\d.,]*(?![A-Za-z0-9])")
FLAG_RE = re.compile(r"[\U0001F1E6-\U0001F1FF]")


class LocalizationError(ValueError):
    """Raised for invalid localization input."""


class ArtifactParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.keys: set[str] = set()
        self.locale_buttons: list[dict[str, Any]] = []
        self._button_stack: list[dict[str, Any]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        key = values.get("data-i18n", "").strip()
        if key:
            self.keys.add(key)
        for binding in values.get("data-i18n-attr", "").split(","):
            if ":" in binding:
                _attribute, binding_key = binding.split(":", 1)
                if binding_key.strip():
                    self.keys.add(binding_key.strip())
        locale = values.get("data-localization-locale", "").strip()
        if tag == "button" and locale:
            record = {
                "locale": locale,
                "role": values.get("role", ""),
                "aria_checked": values.get("aria-checked", ""),
                "aria_label": values.get("aria-label", "").strip(),
                "text": [],
            }
            self.locale_buttons.append(record)
            self._button_stack.append(record)
        elif self._button_stack:
            self._button_stack.append(self._button_stack[-1])

    def handle_endtag(self, tag: str) -> None:
        if self._button_stack:
            self._button_stack.pop()

    def handle_data(self, data: str) -> None:
        if self._button_stack:
            self._button_stack[-1]["text"].append(data)


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LocalizationError(f"invalid manifest {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise LocalizationError("localization manifest must be an object")
    return value


def source_hash(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalized_numbers(value: str) -> Counter[str]:
    normalized: list[str] = []
    for token in NUMBER_RE.findall(value):
        sign = "-" if token.startswith("-") else ""
        digits = re.sub(r"\D", "", token)
        if digits:
            normalized.append(sign + digits)
    return Counter(normalized)


def parse_artifact(path: Path) -> ArtifactParser:
    parser = ArtifactParser()
    try:
        parser.feed(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise LocalizationError(f"cannot read HTML artifact {path}: {exc}") from exc
    return parser


def validate_manifest(
    manifest: dict[str, Any],
    html_paths: list[Path],
    strict_obsolete: bool,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if manifest.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    source_locale = manifest.get("source_locale")
    target_locales = manifest.get("target_locales")
    if not isinstance(source_locale, str) or not source_locale:
        errors.append("source_locale must be a non-empty string")
        source_locale = "en"
    if not isinstance(target_locales, list) or not target_locales or not all(
        isinstance(locale, str) and locale for locale in target_locales
    ):
        errors.append("target_locales must be a non-empty list of locale strings")
        target_locales = []
    all_locales = [source_locale, *target_locales]
    for field in ("default_locale", "fallback_locale"):
        value = manifest.get(field)
        if not isinstance(value, str) or value not in all_locales:
            errors.append(f"{field} must reference source_locale or target_locales")
    if not isinstance(manifest.get("storage_key"), str) or not manifest.get("storage_key", "").strip():
        errors.append("storage_key must be a non-empty string")

    protected_global = manifest.get("protected_terms", [])
    if not isinstance(protected_global, list) or not all(isinstance(item, str) and item for item in protected_global):
        errors.append("protected_terms must be a list of non-empty strings")
        protected_global = []

    messages = manifest.get("messages")
    if not isinstance(messages, dict) or not messages:
        errors.append("messages must be a non-empty object")
        messages = {}

    missing: list[str] = []
    stale: list[str] = []
    preserved_term_errors: list[str] = []
    number_errors: list[str] = []
    for key, record in sorted(messages.items()):
        if not isinstance(key, str) or not key:
            errors.append("message keys must be non-empty strings")
            continue
        if not isinstance(record, dict):
            errors.append(f"{key}: message record must be an object")
            continue
        source = record.get("source")
        stored_hash = record.get("source_hash")
        translations = record.get("translations")
        if not isinstance(source, str) or not source:
            errors.append(f"{key}: source must be a non-empty string")
            continue
        if not isinstance(stored_hash, str) or not HASH_RE.fullmatch(stored_hash):
            errors.append(f"{key}: source_hash must use sha256:<64 lowercase hex>")
        elif stored_hash != source_hash(source):
            stale.append(key)
        if not isinstance(translations, dict):
            errors.append(f"{key}: translations must be an object")
            translations = {}
        local_terms = record.get("protected_terms", [])
        if not isinstance(local_terms, list) or not all(isinstance(item, str) and item for item in local_terms):
            errors.append(f"{key}: protected_terms must be a list of strings")
            local_terms = []
        protected_terms = list(dict.fromkeys([*protected_global, *local_terms]))
        for locale in target_locales:
            translated = translations.get(locale)
            if not isinstance(translated, str) or not translated.strip():
                missing.append(f"{key}:{locale}")
                continue
            for term in protected_terms:
                if term in source and term not in translated:
                    preserved_term_errors.append(f"{key}:{locale}:{term}")
            if record.get("preserve_numbers", True) and normalized_numbers(source) != normalized_numbers(translated):
                number_errors.append(f"{key}:{locale}")

    if missing:
        errors.append("missing translations: " + ", ".join(missing))
    if stale:
        errors.append("stale source hashes: " + ", ".join(stale))
    if preserved_term_errors:
        errors.append("protected terms changed or missing: " + ", ".join(preserved_term_errors))
    if number_errors:
        errors.append("numeric meaning changed: " + ", ".join(number_errors))

    used_keys: set[str] = set()
    locale_controls: set[str] = set()
    for html_path in html_paths:
        parser = parse_artifact(html_path)
        used_keys.update(parser.keys)
        for record in parser.locale_buttons:
            locale = str(record["locale"])
            locale_controls.add(locale)
            visible = FLAG_RE.sub("", "".join(record["text"])).strip()
            accessible_name = visible or str(record["aria_label"])
            if not accessible_name:
                errors.append(f"{html_path}: locale control {locale} has no accessible language name")
            if record["role"] != "radio" or record["aria_checked"] not in {"true", "false"}:
                errors.append(f"{html_path}: locale control {locale} must expose radio role and aria-checked")

    unknown_keys = sorted(used_keys - set(messages))
    obsolete_keys = sorted(set(messages) - used_keys) if html_paths else []
    if unknown_keys:
        errors.append("HTML references unknown localization keys: " + ", ".join(unknown_keys))
    if obsolete_keys:
        message = "manifest keys are not referenced by supplied HTML: " + ", ".join(obsolete_keys)
        (errors if strict_obsolete else warnings).append(message)
    if html_paths:
        expected_controls = set(all_locales)
        missing_controls = sorted(expected_controls - locale_controls)
        if missing_controls:
            errors.append("language switch is missing locale controls: " + ", ".join(missing_controls))

    return {
        "status": "PASS" if not errors else "FAIL",
        "source_locale": source_locale,
        "target_locales": target_locales,
        "message_count": len(messages),
        "used_key_count": len(used_keys),
        "missing_translation_count": len(missing),
        "stale_key_count": len(stale),
        "obsolete_key_count": len(obsolete_keys),
        "errors": errors,
        "warnings": warnings,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--html", type=Path, action="append", default=[])
    parser.add_argument("--strict-obsolete", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_output")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = validate_manifest(load_manifest(args.manifest), args.html, args.strict_obsolete)
    except LocalizationError as exc:
        report = {"status": "FAIL", "errors": [str(exc)], "warnings": []}
    if args.json_output:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(
            f"localization={report['status']} "
            f"messages={report.get('message_count', 0)} "
            f"missing={report.get('missing_translation_count', 0)} "
            f"stale={report.get('stale_key_count', 0)} "
            f"obsolete={report.get('obsolete_key_count', 0)}"
        )
        for warning in report.get("warnings", []):
            print(f"WARNING {warning}")
        for error in report.get("errors", []):
            print(f"ERROR {error}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
