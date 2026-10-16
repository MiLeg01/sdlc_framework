#!/usr/bin/env python3
"""Validate and resolve Agent Commons archetype composition without external dependencies."""

from __future__ import annotations

import argparse
import json
import sys
from collections import OrderedDict
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = ROOT / "archetypes" / "composition.yaml"
CAPABILITY_CATALOG_PATH = ROOT / "catalog" / "capabilities.yaml"


class CompositionError(ValueError):
    """The composition contract or requested selection is invalid."""


@lru_cache(maxsize=None)
def load_json_yaml(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        label = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        raise CompositionError(f"invalid JSON-compatible YAML {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise CompositionError(f"manifest must be an object: {path.relative_to(ROOT)}")
    return value


@lru_cache(maxsize=1)
def load_contract() -> dict[str, Any]:
    return load_json_yaml(CONTRACT_PATH)


@lru_cache(maxsize=1)
def load_capability_catalog() -> dict[str, Any]:
    return load_json_yaml(CAPABILITY_CATALOG_PATH)


def split_values(values: list[str] | None) -> list[str]:
    result: list[str] = []
    for value in values or []:
        for item in value.split(","):
            item = item.strip()
            if item and item not in result:
                result.append(item)
    return result


def registry_aliases(contract: dict[str, Any]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for identifier, entry in contract.get("archetypes", {}).items():
        aliases[identifier] = identifier
        for alias in entry.get("aliases", []):
            if alias in aliases and aliases[alias] != identifier:
                raise CompositionError(f"duplicate archetype alias: {alias}")
            aliases[alias] = identifier
    return aliases


def manifest_path(entry: dict[str, Any]) -> Path:
    return ROOT / "archetypes" / entry["path"]


@lru_cache(maxsize=1)
def _load_manifests_cached() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    contract = load_contract()
    groups: list[dict[str, dict[str, Any]]] = []
    for registry_name in ("archetypes", "overlays"):
        manifests: dict[str, dict[str, Any]] = {}
        for identifier, entry in contract.get(registry_name, {}).items():
            manifests[identifier] = load_json_yaml(manifest_path(entry))
        groups.append(manifests)
    return groups[0], groups[1]


def load_manifests(contract: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    if contract is load_contract() or contract == load_contract():
        return _load_manifests_cached()
    groups: list[dict[str, dict[str, Any]]] = []
    for registry_name in ("archetypes", "overlays"):
        manifests: dict[str, dict[str, Any]] = {}
        for identifier, entry in contract.get(registry_name, {}).items():
            manifests[identifier] = load_json_yaml(manifest_path(entry))
        groups.append(manifests)
    return groups[0], groups[1]


def capability_path(kind: str, identifier: str) -> Path:
    catalog = load_capability_catalog()
    group = catalog.get(kind, {})
    entry = group.get(identifier) if isinstance(group, dict) else None
    if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
        return ROOT / ".missing-capability" / kind / identifier
    return ROOT / entry["path"]


def capability_sets(manifest: dict[str, Any], levels: list[str], kinds: list[str]) -> list[tuple[str, str, str]]:
    result: list[tuple[str, str, str]] = []
    capabilities = manifest.get("capabilities", {})
    for level in levels:
        group = capabilities.get(level, {})
        if not isinstance(group, dict):
            continue
        for kind in kinds:
            values = group.get(kind, [])
            if not isinstance(values, list):
                continue
            for identifier in values:
                result.append((level, kind, identifier))
    return result


@lru_cache(maxsize=1)
def validate_contract() -> list[str]:
    errors: list[str] = []
    try:
        contract = load_contract()
    except CompositionError as exc:
        return [str(exc)]
    if contract.get("schema_version") != 1:
        errors.append("composition schema_version must be 1")
    try:
        catalog = load_capability_catalog()
    except CompositionError as exc:
        return errors + [str(exc)]
    if catalog.get("schema_version") != 1:
        errors.append("capability catalog schema_version must be 1")
    if contract.get("manifest_format") != "json-compatible-yaml":
        errors.append("composition manifest_format must be json-compatible-yaml")
    levels = contract.get("capability_levels")
    kinds = contract.get("capability_kinds")
    if levels != ["required", "default", "recommended", "optional"]:
        errors.append("capability_levels must preserve required/default/recommended/optional precedence")
        levels = ["required", "default", "recommended", "optional"]
    if kinds != ["skills", "agents", "tools", "templates"]:
        errors.append("capability_kinds must be skills/agents/tools/templates")
        kinds = ["skills", "agents", "tools", "templates"]
    if catalog.get("capability_kinds") != kinds:
        errors.append("capability catalog kinds must match the composition contract")
    if contract.get("default_levels") != ["required", "default"]:
        errors.append("default_levels must be required/default")
    resolution = contract.get("resolution", {})
    if resolution.get("deduplicate_by") != ["capability_kind", "capability_id"]:
        errors.append("resolution deduplicate_by must use capability kind and id")
    if resolution.get("level_precedence") != levels:
        errors.append("resolution level_precedence must match capability_levels")
    if resolution.get("source_order") != ["base", "archetypes", "overlays", "activated_conditions"]:
        errors.append("resolution source_order is invalid")
    if resolution.get("explicit_exclusions") != "remove only explicitly named default or recommended capabilities; required capabilities cannot be excluded":
        errors.append("resolution explicit_exclusions is invalid")
    global_conditions: dict[str, str] = {}
    for registry_name, expected_kind in (("archetypes", "archetype"), ("overlays", "overlay")):
        registry = contract.get(registry_name)
        if not isinstance(registry, dict) or not registry:
            errors.append(f"{registry_name} registry must be a non-empty object")
            continue
        paths: set[str] = set()
        for identifier, entry in registry.items():
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                errors.append(f"{registry_name}.{identifier} must define a path")
                continue
            if entry["path"] in paths:
                errors.append(f"duplicate manifest path: {entry['path']}")
            paths.add(entry["path"])
            path = manifest_path(entry)
            if not path.is_file():
                errors.append(f"missing {expected_kind} manifest: {path.relative_to(ROOT)}")
                continue
            try:
                manifest = load_json_yaml(path)
            except CompositionError as exc:
                errors.append(str(exc))
                continue
            if manifest.get("schema_version") != 1:
                errors.append(f"{identifier}: schema_version must be 1")
            if manifest.get("id") != identifier:
                errors.append(f"{identifier}: manifest id does not match registry")
            if manifest.get("kind") != expected_kind:
                errors.append(f"{identifier}: kind must be {expected_kind}")
            capabilities = manifest.get("capabilities")
            if not isinstance(capabilities, dict) or set(capabilities) != set(levels):
                errors.append(f"{identifier}: capabilities must define exactly {levels}")
                continue
            for level in levels:
                group = capabilities[level]
                if not isinstance(group, dict) or set(group) != set(kinds):
                    errors.append(f"{identifier}:{level}: capability group must define exactly {kinds}")
                    continue
                for kind in kinds:
                    if not isinstance(group[kind], list):
                        errors.append(f"{identifier}:{level}: {kind} must be a list")
            seen_manifest: dict[tuple[str, str], str] = {}
            for level, kind, capability in capability_sets(manifest, levels, kinds):
                if not isinstance(capability, str) or not capability:
                    errors.append(f"{identifier}: invalid {kind} capability id")
                    continue
                key = (kind, capability)
                if key in seen_manifest:
                    errors.append(
                        f"{identifier}: {kind}/{capability} appears in both {seen_manifest[key]} and {level}"
                    )
                seen_manifest[key] = level
                if not capability_path(kind, capability).exists():
                    errors.append(f"{identifier}: missing referenced {kind[:-1]} {capability}")
            condition_ids: set[str] = set()
            for condition in manifest.get("conditions", []):
                condition_id = condition.get("id") if isinstance(condition, dict) else None
                if not condition_id or condition_id in condition_ids:
                    errors.append(f"{identifier}: condition ids must be non-empty and unique")
                    continue
                condition_ids.add(condition_id)
                if condition_id in global_conditions:
                    errors.append(
                        f"condition id {condition_id} is ambiguous between {global_conditions[condition_id]} and {identifier}"
                    )
                else:
                    global_conditions[condition_id] = identifier
                group = condition.get("capabilities", {})
                if set(group) != set(kinds):
                    errors.append(f"{identifier}:{condition_id}: conditional capabilities must define {kinds}")
                    continue
                for kind in kinds:
                    values = group.get(kind)
                    if not isinstance(values, list):
                        errors.append(f"{identifier}:{condition_id}: {kind} must be a list")
                        continue
                    for capability in values:
                        if not capability_path(kind, capability).exists():
                            errors.append(f"{identifier}:{condition_id}: missing referenced {kind[:-1]} {capability}")
            if "includes" in manifest:
                errors.append(f"{identifier}: nested includes are forbidden; compose hybrids at the root")
            if expected_kind == "overlay":
                compatible = manifest.get("compatible_archetypes", [])
                if len(set(compatible)) < 2:
                    errors.append(f"{identifier}: overlay must apply to at least two archetypes")
                unknown = sorted(set(compatible) - set(contract.get("archetypes", {})))
                if unknown:
                    errors.append(f"{identifier}: unknown compatible archetypes {unknown}")
            else:
                for recommendation in manifest.get("recommended_overlays", []):
                    overlay_id = recommendation.get("id") if isinstance(recommendation, dict) else None
                    if overlay_id not in contract.get("overlays", {}):
                        errors.append(f"{identifier}: unknown recommended overlay {overlay_id}")
                    else:
                        overlay = load_json_yaml(manifest_path(contract["overlays"][overlay_id]))
                        if identifier not in overlay.get("compatible_archetypes", []):
                            errors.append(f"{identifier}: recommended overlay {overlay_id} is incompatible")
                for recommendation in manifest.get("recommended_compositions", []):
                    archetype_id = recommendation.get("id") if isinstance(recommendation, dict) else None
                    if archetype_id not in contract.get("archetypes", {}):
                        errors.append(f"{identifier}: unknown recommended archetype {archetype_id}")
    try:
        registry_aliases(contract)
    except CompositionError as exc:
        errors.append(str(exc))
    return errors


def resolve_composition(
    archetypes: list[str],
    overlays: list[str] | None = None,
    conditions: list[str] | None = None,
    scale: str = "standard",
    include_recommended: bool = False,
    exclude_skills: list[str] | None = None,
) -> dict[str, Any]:
    errors = validate_contract()
    if errors:
        raise CompositionError("invalid archetype contract:\n- " + "\n- ".join(errors))
    contract = load_contract()
    archetype_manifests, overlay_manifests = load_manifests(contract)
    aliases = registry_aliases(contract)
    selected_archetypes: list[str] = []
    for identifier in archetypes:
        canonical = aliases.get(identifier)
        if canonical is None:
            raise CompositionError(f"unknown archetype: {identifier}")
        if canonical not in selected_archetypes:
            selected_archetypes.append(canonical)
    if not selected_archetypes:
        raise CompositionError("at least one archetype is required")
    selected_overlays: list[str] = []
    for identifier in overlays or []:
        if identifier not in overlay_manifests:
            raise CompositionError(f"unknown overlay: {identifier}")
        compatible = set(overlay_manifests[identifier]["compatible_archetypes"])
        if not compatible.intersection(selected_archetypes):
            raise CompositionError(f"overlay {identifier} is not compatible with the selected archetypes")
        if identifier not in selected_overlays:
            selected_overlays.append(identifier)
    if scale not in {"tiny", "standard"}:
        raise CompositionError(f"unknown scale: {scale}")
    levels = list(contract["default_levels"])
    if include_recommended:
        levels.append("recommended")
    kinds = contract["capability_kinds"]
    selected: dict[str, OrderedDict[str, dict[str, Any]]] = {kind: OrderedDict() for kind in kinds}

    def add(kind: str, identifier: str, level: str, source: str) -> None:
        current = selected[kind].get(identifier)
        precedence = contract["resolution"]["level_precedence"]
        if current is None:
            selected[kind][identifier] = {"level": level, "sources": [source]}
            return
        if source not in current["sources"]:
            current["sources"].append(source)
        if precedence.index(level) < precedence.index(current["level"]):
            current["level"] = level

    for kind, values in contract["base"]["capabilities"].items():
        for identifier in values:
            add(kind, identifier, "required", "base")
    for identifier in selected_archetypes:
        manifest = archetype_manifests[identifier]
        active_levels = ["required"] if scale == "tiny" else levels
        for level, kind, capability in capability_sets(manifest, active_levels, kinds):
            add(kind, capability, level, f"archetype:{identifier}")
    for identifier in selected_overlays:
        manifest = overlay_manifests[identifier]
        for level, kind, capability in capability_sets(manifest, levels, kinds):
            add(kind, capability, level, f"overlay:{identifier}")
    available_conditions: dict[str, tuple[str, dict[str, Any]]] = {}
    for identifier in selected_archetypes:
        for condition in archetype_manifests[identifier].get("conditions", []):
            available_conditions[condition["id"]] = (f"archetype:{identifier}", condition)
    for identifier in selected_overlays:
        for condition in overlay_manifests[identifier].get("conditions", []):
            available_conditions[condition["id"]] = (f"overlay:{identifier}", condition)
    selected_conditions: list[str] = []
    for condition_id in conditions or []:
        if condition_id not in available_conditions:
            raise CompositionError(f"unknown condition for selected composition: {condition_id}")
        source, condition = available_conditions[condition_id]
        selected_conditions.append(condition_id)
        for kind in kinds:
            for capability in condition["capabilities"][kind]:
                add(kind, capability, "default", f"condition:{condition_id}@{source}")
    excluded: list[str] = []
    for identifier in exclude_skills or []:
        current = selected["skills"].get(identifier)
        if current is None:
            continue
        if current["level"] == "required":
            raise CompositionError(f"cannot exclude required skill: {identifier}")
        del selected["skills"][identifier]
        excluded.append(identifier)
    return {
        "schema_version": contract["schema_version"],
        "scale": scale,
        "archetypes": selected_archetypes,
        "overlays": selected_overlays,
        "conditions": selected_conditions,
        "levels": levels,
        "excluded_skills": excluded,
        "capabilities": {kind: list(entries) for kind, entries in selected.items()},
        "provenance": {kind: entries for kind, entries in selected.items()},
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="validate all archetype and overlay manifests")
    resolve = subparsers.add_parser("resolve", help="resolve a composition to deduplicated capabilities")
    resolve.add_argument("--archetype", action="append", required=True)
    resolve.add_argument("--overlay", action="append", default=[])
    resolve.add_argument("--condition", action="append", default=[])
    resolve.add_argument("--scale", choices=["standard", "tiny"], default="standard")
    resolve.add_argument("--include-recommended", action="store_true")
    resolve.add_argument("--exclude-skill", action="append", default=[])
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "validate":
            errors = validate_contract()
            contract = load_contract()
            print(
                f"archetypes={len(contract.get('archetypes', {}))} "
                f"overlays={len(contract.get('overlays', {}))} errors={len(errors)}"
            )
            for error in errors:
                print(f"ERROR {error}")
            return 1 if errors else 0
        resolved = resolve_composition(
            split_values(args.archetype),
            split_values(args.overlay),
            split_values(args.condition),
            args.scale,
            args.include_recommended,
            split_values(args.exclude_skill),
        )
        print(json.dumps(resolved, indent=2, ensure_ascii=False))
        return 0
    except CompositionError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
