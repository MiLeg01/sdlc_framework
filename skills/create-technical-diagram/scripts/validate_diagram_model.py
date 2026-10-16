#!/usr/bin/env python3
"""Validate a lightweight evidence-backed technical-diagram model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DIAGRAM_TYPES = {
    "system-landscape",
    "component-architecture",
    "class",
    "er",
    "sequence",
    "data-flow",
    "migration-roadmap",
}
CONFIDENCE = {"VERIFIED", "INFERRED", "UNKNOWN"}
DIAGRAM_STATUS = {"CURRENT", "TARGET", "TRANSITION", "COMPARISON", "PROPOSED", "DRAFT", "FINAL"}
MAX_VIEW_NODES = 40
MAX_VIEW_RELATIONSHIPS = 60


class DiagramModelError(ValueError):
    """The diagram model is unreadable or structurally invalid."""


def load_model(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DiagramModelError(str(exc)) from exc
    if not isinstance(value, dict):
        raise DiagramModelError("model root must be an object")
    return value


def objects(value: object, label: str, errors: list[str]) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return []
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            errors.append(f"{label}[{index}] must be an object")
        else:
            result.append(item)
    return result


def unique_ids(entries: list[dict[str, Any]], label: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries):
        identifier = entry.get("id")
        if not isinstance(identifier, str) or not identifier.strip():
            errors.append(f"{label}[{index}].id must be a non-empty string")
            continue
        if identifier in result:
            errors.append(f"duplicate {label} id: {identifier}")
            continue
        result[identifier] = entry
    return result


def string_list(value: object, label: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        errors.append(f"{label} must be a list of non-empty strings")
        return []
    return list(value)


def validate_confidence(
    entry: dict[str, Any],
    label: str,
    evidence_ids: set[str],
    errors: list[str],
    relationship: bool = False,
) -> None:
    confidence = entry.get("confidence")
    if confidence not in CONFIDENCE:
        errors.append(f"{label}.confidence must be one of {sorted(CONFIDENCE)}")
        return
    refs = string_list(entry.get("evidence_ids", []), f"{label}.evidence_ids", errors)
    unknown_refs = sorted(set(refs) - evidence_ids)
    if unknown_refs:
        errors.append(f"{label} references unknown evidence ids: {unknown_refs}")
    rationale = entry.get("rationale")
    if confidence == "VERIFIED" and not refs:
        errors.append(f"{label} is VERIFIED but has no evidence_ids")
    if confidence == "INFERRED" and (not refs or not isinstance(rationale, str) or not rationale.strip()):
        errors.append(f"{label} is INFERRED and requires evidence_ids plus rationale")
    if confidence == "UNKNOWN":
        annotation = entry.get("annotation")
        if not isinstance(annotation, str) or not annotation.strip():
            errors.append(f"{label} is UNKNOWN and requires an annotation")
        if relationship and entry.get("include", True):
            errors.append(f"{label} is UNKNOWN and must set include=false rather than render a normal edge")


def validate(model: dict[str, Any]) -> tuple[list[str], list[str], dict[str, int]]:
    errors: list[str] = []
    warnings: list[str] = []
    if model.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    diagram = model.get("diagram")
    if not isinstance(diagram, dict):
        errors.append("diagram must be an object")
        diagram = {}
    if diagram.get("type") not in DIAGRAM_TYPES:
        errors.append(f"diagram.type must be one of {sorted(DIAGRAM_TYPES)}")
    for field in ("title", "purpose", "scope"):
        if not isinstance(diagram.get(field), str) or not str(diagram.get(field)).strip():
            errors.append(f"diagram.{field} must be a non-empty string")
    audience = diagram.get("audience")
    if not isinstance(audience, list) or not audience or any(not isinstance(item, str) or not item for item in audience):
        errors.append("diagram.audience must be a non-empty list of strings")
    if diagram.get("status") not in DIAGRAM_STATUS:
        errors.append(f"diagram.status must be one of {sorted(DIAGRAM_STATUS)}")

    evidence = objects(model.get("evidence", []), "evidence", errors)
    evidence_by_id = unique_ids(evidence, "evidence", errors)
    for identifier, entry in evidence_by_id.items():
        if not isinstance(entry.get("source"), str) or not entry["source"].strip():
            errors.append(f"evidence {identifier}.source must be a non-empty string")
        if not isinstance(entry.get("locator"), str) or not entry["locator"].strip():
            errors.append(f"evidence {identifier}.locator must be a non-empty string")

    nodes = objects(model.get("nodes", []), "nodes", errors)
    relationships = objects(model.get("relationships", []), "relationships", errors)
    views = objects(model.get("views", []), "views", errors)
    node_by_id = unique_ids(nodes, "nodes", errors)
    relationship_by_id = unique_ids(relationships, "relationships", errors)
    view_by_id = unique_ids(views, "views", errors)

    for identifier, node in node_by_id.items():
        if not isinstance(node.get("label"), str) or not node["label"].strip():
            errors.append(f"node {identifier}.label must be a non-empty string")
        if not isinstance(node.get("kind"), str) or not node["kind"].strip():
            errors.append(f"node {identifier}.kind must be a non-empty string")
        validate_confidence(node, f"node {identifier}", set(evidence_by_id), errors)

    for identifier, relationship in relationship_by_id.items():
        source = relationship.get("source")
        target = relationship.get("target")
        if source not in node_by_id:
            errors.append(f"relationship {identifier} has unknown source node: {source}")
        if target not in node_by_id:
            errors.append(f"relationship {identifier} has unknown target node: {target}")
        if source == target and source is not None:
            warnings.append(f"relationship {identifier} is self-referential")
        if not isinstance(relationship.get("label"), str) or not relationship["label"].strip():
            errors.append(f"relationship {identifier}.label must be a non-empty string")
        validate_confidence(
            relationship,
            f"relationship {identifier}",
            set(evidence_by_id),
            errors,
            relationship=True,
        )

    included_nodes = {identifier for identifier, node in node_by_id.items() if node.get("include", True)}
    included_relationships = {
        identifier for identifier, relationship in relationship_by_id.items() if relationship.get("include", True)
    }
    for identifier in included_relationships:
        relationship = relationship_by_id[identifier]
        if relationship.get("source") not in included_nodes or relationship.get("target") not in included_nodes:
            errors.append(f"included relationship {identifier} has an excluded endpoint")

    if not view_by_id:
        if len(included_nodes) > MAX_VIEW_NODES or len(included_relationships) > MAX_VIEW_RELATIONSHIPS:
            errors.append(
                "large model requires overview/drilldown views "
                f"(nodes>{MAX_VIEW_NODES} or relationships>{MAX_VIEW_RELATIONSHIPS})"
            )
    else:
        covered_nodes: set[str] = set()
        covered_relationships: set[str] = set()
        for identifier, view in view_by_id.items():
            if not isinstance(view.get("title"), str) or not view["title"].strip():
                errors.append(f"view {identifier}.title must be a non-empty string")
            node_ids = string_list(view.get("node_ids", []), f"view {identifier}.node_ids", errors)
            relationship_ids = string_list(
                view.get("relationship_ids", []), f"view {identifier}.relationship_ids", errors
            )
            unknown_nodes = sorted(set(node_ids) - set(node_by_id))
            unknown_relationships = sorted(set(relationship_ids) - set(relationship_by_id))
            if unknown_nodes:
                errors.append(f"view {identifier} references unknown nodes: {unknown_nodes}")
            if unknown_relationships:
                errors.append(f"view {identifier} references unknown relationships: {unknown_relationships}")
            if len(node_ids) > MAX_VIEW_NODES:
                errors.append(f"view {identifier} exceeds {MAX_VIEW_NODES} nodes")
            if len(relationship_ids) > MAX_VIEW_RELATIONSHIPS:
                errors.append(f"view {identifier} exceeds {MAX_VIEW_RELATIONSHIPS} relationships")
            visible = set(node_ids)
            for relationship_id in relationship_ids:
                relationship = relationship_by_id.get(relationship_id, {})
                if relationship.get("source") not in visible or relationship.get("target") not in visible:
                    errors.append(f"view {identifier} relationship {relationship_id} has an endpoint outside the view")
            covered_nodes.update(set(node_ids) & included_nodes)
            covered_relationships.update(set(relationship_ids) & included_relationships)
        missing_nodes = sorted(included_nodes - covered_nodes)
        missing_relationships = sorted(included_relationships - covered_relationships)
        if missing_nodes:
            errors.append(f"included nodes are absent from all views: {missing_nodes}")
        if missing_relationships:
            errors.append(f"included relationships are absent from all views: {missing_relationships}")

    counts = {
        "evidence": len(evidence_by_id),
        "nodes": len(node_by_id),
        "relationships": len(relationship_by_id),
        "views": len(view_by_id),
        "included_nodes": len(included_nodes),
        "included_relationships": len(included_relationships),
    }
    return errors, warnings, counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path)
    parser.add_argument("--strict-warnings", action="store_true")
    args = parser.parse_args()
    try:
        model = load_model(args.model)
    except DiagramModelError as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)], "warnings": [], "counts": {}}, indent=2))
        return 1
    errors, warnings, counts = validate(model)
    print(json.dumps({"valid": not errors, "errors": errors, "warnings": warnings, "counts": counts}, indent=2))
    return 1 if errors or (args.strict_warnings and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
