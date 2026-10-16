#!/usr/bin/env python3
"""Resolve project capability requirements against the actual Agent Commons catalog."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from resolve_archetypes import (
    CompositionError,
    load_capability_catalog,
    load_contract,
    load_manifests,
    resolve_composition,
    split_values,
)


ROOT = Path(__file__).resolve().parent.parent
STATUSES = {"COVERED", "PARTIALLY_COVERED", "MISSING", "OPTIONAL_GAP"}
IMPORTANCE_ORDER = ("required", "strongly_recommended", "optional")
IMPORTANCE_LEVELS = set(IMPORTANCE_ORDER)
MATERIAL_STATUSES = {"PARTIALLY_COVERED", "MISSING"}


class CapabilityGapError(ValueError):
    """The capability expectation contract or requested assessment is invalid."""


def slug(value: str) -> str:
    normalized = value.strip().lower()
    normalized = normalized.replace("pl/i", "pli").replace("c#", "csharp").replace("c++", "cpp")
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return normalized


def catalog_providers(catalog: dict[str, Any]) -> dict[str, list[str]]:
    providers: dict[str, list[str]] = {}
    for kind in catalog.get("capability_kinds", []):
        entries = catalog.get(kind, {})
        if not isinstance(entries, dict):
            continue
        for identifier, metadata in entries.items():
            if not isinstance(metadata, dict):
                continue
            for semantic_id in metadata.get("provides", []):
                if isinstance(semantic_id, str) and semantic_id:
                    providers.setdefault(semantic_id, []).append(f"{kind}:{identifier}")
    return providers


def selected_providers(composition: dict[str, Any], catalog: dict[str, Any]) -> dict[str, list[str]]:
    providers: dict[str, list[str]] = {}
    capabilities = composition.get("capabilities", {})
    for kind in catalog.get("capability_kinds", []):
        entries = catalog.get(kind, {})
        selected = capabilities.get(kind, []) if isinstance(capabilities, dict) else []
        for identifier in selected:
            metadata = entries.get(identifier, {}) if isinstance(entries, dict) else {}
            for semantic_id in metadata.get("provides", []) if isinstance(metadata, dict) else []:
                providers.setdefault(semantic_id, []).append(f"{kind}:{identifier}")
    return providers


def requested_text(values: list[str]) -> str:
    return " ".join(values).lower()


def condition_is_active(
    condition: str,
    *,
    source: str,
    target: str,
    scopes: list[str],
    overlays: list[str],
    goal: str,
    deliverables: list[str],
    validation: list[str],
) -> bool:
    text = requested_text([goal, *deliverables])
    if condition == "always":
        return True
    if condition == "migration-target-declared":
        return bool(target)
    if condition == "target-implementation-selected":
        return bool(target) and "development" in scopes
    if condition == "requirements-requested":
        return "evidence-traceability" in overlays or any(word in text for word in ("requirement", "business rule"))
    if condition == "traceability-requested":
        return "evidence-traceability" in overlays or "traceab" in text or "provenance" in text
    if condition == "validation-requested":
        validation_text = requested_text([*validation, text])
        return bool(validation) or any(word in validation_text for word in ("parity", "validation", "verification", "acceptance"))
    raise CapabilityGapError(f"unknown capability expectation condition: {condition}")


def assessment_entry(
    identifier: str,
    importance: str,
    description: str,
    providers: dict[str, list[str]],
    *,
    dimension: str = "generic",
    exact_requirement: str | None = None,
    generic_fallback: str | None = None,
    specialist_required: bool = False,
) -> dict[str, Any]:
    exact_id = exact_requirement or identifier
    exact_providers = providers.get(exact_id, [])
    fallback_providers = providers.get(generic_fallback, []) if generic_fallback else []
    if exact_providers:
        status = "COVERED"
        covered_by = exact_providers
    elif importance == "optional":
        status = "OPTIONAL_GAP"
        covered_by = fallback_providers
    elif fallback_providers and not specialist_required:
        status = "PARTIALLY_COVERED"
        covered_by = fallback_providers
    else:
        status = "MISSING"
        covered_by = fallback_providers
    result = {
        "id": identifier,
        "status": status,
        "importance": importance,
        "dimension": dimension,
        "description": description,
        "covered_by": covered_by,
    }
    if exact_requirement:
        result["exact_requirement"] = exact_requirement
    if generic_fallback:
        result["generic_fallback"] = generic_fallback
    return result


def gap_queries(entries: list[dict[str, Any]], source: str, target: str) -> list[str]:
    queries: list[str] = []
    source_label = source.strip()
    target_label = target.strip()
    for entry in entries:
        if entry["status"] not in MATERIAL_STATUSES:
            continue
        dimension = entry.get("dimension")
        if dimension == "source" and source_label:
            queries.extend([
                f"{source_label} code semantic analysis agent skill",
                f"{source_label} business rule and dependency extraction workflow",
            ])
        elif dimension == "target" and target_label:
            queries.append(f"{target_label} modernization target architecture agent workflow")
        elif dimension == "bridge" and source_label and target_label:
            queries.extend([
                f"{source_label} to {target_label} migration mapping workflow",
                f"{source_label} modernization validation {target_label}",
            ])
        elif entry["id"] == "generic-migration-planning":
            queries.append("legacy migration planning agent workflow")
        elif entry["id"] == "requirements-extraction":
            queries.append("legacy business rule requirements extraction agent workflow")
        elif entry["id"] == "migration-validation":
            queries.append("legacy modernization parity validation agent workflow")
    return list(dict.fromkeys(queries))[:8]


def assess(
    composition: dict[str, Any],
    *,
    source: str = "",
    target: str = "",
    goal: str = "",
    deliverables: list[str] | None = None,
    validation: list[str] | None = None,
) -> dict[str, Any]:
    catalog = load_capability_catalog()
    contract = load_contract()
    archetype_manifests, _ = load_manifests(contract)
    providers = selected_providers(composition, catalog)
    entries: list[dict[str, Any]] = []
    scopes = composition.get("archetypes", [])
    overlays = composition.get("overlays", [])
    deliverables = deliverables or []
    validation = validation or []

    for archetype_id in scopes:
        expectations = archetype_manifests[archetype_id].get("capability_expectations", {})
        for importance in ("required", "strongly_recommended", "optional"):
            for expectation in expectations.get(importance, []):
                if not condition_is_active(
                    expectation["when"],
                    source=source,
                    target=target,
                    scopes=scopes,
                    overlays=overlays,
                    goal=goal,
                    deliverables=deliverables,
                    validation=validation,
                ):
                    continue
                entries.append(assessment_entry(
                    expectation["id"],
                    importance,
                    expectation["description"],
                    providers,
                ))

        dimensions = expectations.get("migration_dimensions", {})
        source_slug = slug(source) if source else ""
        target_slug = slug(target) if target else ""
        if source_slug and "source" in dimensions:
            spec = dimensions["source"]
            exact = spec["exact_template"].format(source=source_slug, target=target_slug)
            entries.append(assessment_entry(
                f"{source_slug}-semantic-analysis",
                spec["importance"],
                spec["description"],
                providers,
                dimension="source",
                exact_requirement=exact,
                generic_fallback=spec["generic"],
                specialist_required=True,
            ))
        if target_slug and "target" in dimensions:
            spec = dimensions["target"]
            exact = spec["exact_template"].format(source=source_slug, target=target_slug)
            entries.append(assessment_entry(
                f"{target_slug}-target-architecture",
                spec["importance"],
                spec["description"],
                providers,
                dimension="target",
                exact_requirement=exact,
                generic_fallback=spec["generic"],
            ))
        if source_slug and target_slug and "bridge" in dimensions:
            spec = dimensions["bridge"]
            exact = spec["exact_template"].format(source=source_slug, target=target_slug)
            entries.append(assessment_entry(
                f"{source_slug}-to-{target_slug}-mapping",
                spec["importance"],
                spec["description"],
                providers,
                dimension="bridge",
                exact_requirement=exact,
                generic_fallback=spec["generic"],
                specialist_required=True,
            ))

    deduplicated: dict[str, dict[str, Any]] = {}
    for entry in entries:
        current = deduplicated.get(entry["id"])
        if current is None or IMPORTANCE_ORDER.index(entry["importance"]) < IMPORTANCE_ORDER.index(current["importance"]):
            deduplicated[entry["id"]] = entry
    entries = list(deduplicated.values())
    meaningful = [
        entry for entry in entries
        if entry["importance"] != "optional" and entry["status"] in MATERIAL_STATUSES
    ]
    return {
        "schema_version": 1,
        "source_technology": source or None,
        "target_technology": target or None,
        "coverage": [entry for entry in entries if entry["status"] == "COVERED"],
        "gaps": [entry for entry in entries if entry["status"] != "COVERED"],
        "meaningful_gaps": meaningful,
        "requires_user_choice": bool(meaningful),
        "search_queries": gap_queries(meaningful, source, target),
    }


def validate_expectations() -> list[str]:
    errors: list[str] = []
    catalog = load_capability_catalog()
    all_providers = catalog_providers(catalog)
    contract = load_contract()
    archetype_manifests, _ = load_manifests(contract)
    for archetype_id, manifest in archetype_manifests.items():
        expectations = manifest.get("capability_expectations")
        if expectations is None:
            continue
        for importance in ("required", "strongly_recommended", "optional"):
            group = expectations.get(importance)
            if not isinstance(group, list):
                errors.append(f"{archetype_id}: capability_expectations.{importance} must be a list")
                continue
            for entry in group:
                if not isinstance(entry, dict) or not all(isinstance(entry.get(key), str) for key in ("id", "when", "description")):
                    errors.append(f"{archetype_id}: invalid {importance} capability expectation")
                    continue
                if entry["id"] not in all_providers and importance != "optional":
                    errors.append(f"{archetype_id}: no commons capability provides semantic id {entry['id']}")
                try:
                    condition_is_active(
                        entry["when"], source="", target="", scopes=[], overlays=[], goal="",
                        deliverables=[], validation=[],
                    )
                except CapabilityGapError as exc:
                    errors.append(f"{archetype_id}: {exc}")
        dimensions = expectations.get("migration_dimensions", {})
        if dimensions and set(dimensions) != {"source", "target", "bridge"}:
            errors.append(f"{archetype_id}: migration_dimensions must define source, target, and bridge")
        for dimension, entry in dimensions.items():
            if entry.get("importance") not in IMPORTANCE_LEVELS:
                errors.append(f"{archetype_id}:{dimension}: invalid importance")
            if not all(isinstance(entry.get(key), str) for key in ("exact_template", "generic", "description")):
                errors.append(f"{archetype_id}:{dimension}: invalid migration dimension")
            elif entry["generic"] not in all_providers:
                errors.append(f"{archetype_id}:{dimension}: unknown generic semantic capability {entry['generic']}")
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")
    resolve = subparsers.add_parser("resolve")
    resolve.add_argument("--archetype", action="append", required=True)
    resolve.add_argument("--overlay", action="append", default=[])
    resolve.add_argument("--condition", action="append", default=[])
    resolve.add_argument("--scale", choices=["standard", "tiny"], default="standard")
    resolve.add_argument("--source-technology", default="")
    resolve.add_argument("--target-technology", default="")
    resolve.add_argument("--goal", default="")
    resolve.add_argument("--deliverable", action="append", default=[])
    resolve.add_argument("--validation", action="append", default=[])
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "validate":
            errors = validate_expectations()
            print(f"capability_expectations errors={len(errors)}")
            for error in errors:
                print(f"ERROR {error}")
            return 1 if errors else 0
        composition = resolve_composition(
            split_values(args.archetype),
            split_values(args.overlay),
            split_values(args.condition),
            args.scale,
        )
        result = assess(
            composition,
            source=args.source_technology,
            target=args.target_technology,
            goal=args.goal,
            deliverables=args.deliverable,
            validation=args.validation,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (CapabilityGapError, CompositionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
