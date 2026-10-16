#!/usr/bin/env python3
"""Audit a normalized delivery traceability graph."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SEVERITIES = {"critical", "major", "warning", "info"}
SEVERITY_ORDER = {"critical": 0, "major": 1, "warning": 2, "info": 3}


def require_list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"{key} must be an array")
    return value


def require_text(item: dict[str, Any], key: str, context: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}.{key} must be a non-empty string")
    return value.strip()


def audit(payload: object) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("graph must be a JSON object")
    if payload.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")

    nodes = require_list(payload, "nodes")
    edges = require_list(payload, "edges")
    lifecycle_rules = require_list(payload, "lifecycle_rules")
    generated_views = require_list(payload, "generated_views")
    raw_findings: list[dict[str, str]] = []

    def finding(severity: str, code: str, subject: str, detail: str) -> None:
        if severity not in SEVERITIES:
            raise ValueError(f"unsupported severity: {severity}")
        raw_findings.append(
            {"severity": severity, "code": code, "subject": subject, "detail": detail}
        )

    node_by_id: dict[str, dict[str, Any]] = {}
    for index, raw_node in enumerate(nodes):
        if not isinstance(raw_node, dict):
            raise ValueError(f"nodes[{index}] must be an object")
        node_id = require_text(raw_node, "id", f"nodes[{index}]")
        require_text(raw_node, "type", f"nodes[{index}]")
        if node_id in node_by_id:
            finding("major", "DUPLICATE_NODE_ID", node_id, "Node ID is not unique")
            continue
        node_by_id[node_id] = raw_node

    normalized_edges: list[dict[str, str]] = []
    edge_keys: set[tuple[str, str, str]] = set()
    for index, raw_edge in enumerate(edges):
        if not isinstance(raw_edge, dict):
            raise ValueError(f"edges[{index}] must be an object")
        source = require_text(raw_edge, "source", f"edges[{index}]")
        target = require_text(raw_edge, "target", f"edges[{index}]")
        edge_type = require_text(raw_edge, "type", f"edges[{index}]")
        reciprocal = raw_edge.get("reciprocal_type", "")
        if not isinstance(reciprocal, str):
            raise ValueError(f"edges[{index}].reciprocal_type must be a string")
        normalized = {
            "source": source,
            "target": target,
            "type": edge_type,
            "reciprocal_type": reciprocal.strip(),
        }
        normalized_edges.append(normalized)
        key = (source, target, edge_type)
        if key in edge_keys:
            finding(
                "major",
                "DUPLICATE_EDGE",
                f"{source}->{target}:{edge_type}",
                "Edge triple is not unique",
            )
        edge_keys.add(key)
        if source not in node_by_id:
            finding("major", "MISSING_ENDPOINT", source, f"Edge source for {edge_type} is missing")
        if target not in node_by_id:
            finding("major", "MISSING_ENDPOINT", target, f"Edge target for {edge_type} is missing")

    for edge in normalized_edges:
        reciprocal_type = edge["reciprocal_type"]
        if not reciprocal_type:
            continue
        reciprocal_key = (edge["target"], edge["source"], reciprocal_type)
        if reciprocal_key not in edge_keys:
            finding(
                "major",
                "MISSING_RECIPROCAL",
                f"{edge['source']}->{edge['target']}:{edge['type']}",
                f"Expected reverse edge {edge['target']}->{edge['source']}:{reciprocal_type}",
            )

    for index, raw_rule in enumerate(lifecycle_rules):
        if not isinstance(raw_rule, dict):
            raise ValueError(f"lifecycle_rules[{index}] must be an object")
        context = f"lifecycle_rules[{index}]"
        rule_id = require_text(raw_rule, "id", context)
        node_type = require_text(raw_rule, "node_type", context)
        direction = require_text(raw_rule, "direction", context)
        if direction not in {"in", "out"}:
            raise ValueError(f"{context}.direction must be in or out")
        edge_type = require_text(raw_rule, "edge_type", context)
        related_type = require_text(raw_rule, "related_type", context)
        statuses = raw_rule.get("statuses")
        if not isinstance(statuses, list) or not statuses or any(
            not isinstance(status, str) or not status.strip() for status in statuses
        ):
            raise ValueError(f"{context}.statuses must be a non-empty string array")
        status_set = {status.strip() for status in statuses}
        min_count = raw_rule.get("min_count", 1)
        if not isinstance(min_count, int) or isinstance(min_count, bool) or min_count < 1:
            raise ValueError(f"{context}.min_count must be a positive integer")
        severity = raw_rule.get("severity", "major")
        if not isinstance(severity, str) or severity not in SEVERITIES:
            raise ValueError(f"{context}.severity must be one of {sorted(SEVERITIES)}")

        for node_id, node in sorted(node_by_id.items()):
            if node.get("type") != node_type or node.get("status") not in status_set:
                continue
            matches = 0
            for edge in normalized_edges:
                if edge["type"] != edge_type:
                    continue
                related_id = ""
                if direction == "out" and edge["source"] == node_id:
                    related_id = edge["target"]
                elif direction == "in" and edge["target"] == node_id:
                    related_id = edge["source"]
                related = node_by_id.get(related_id)
                if related and related.get("type") == related_type:
                    matches += 1
            if matches < min_count:
                finding(
                    severity,
                    "LIFECYCLE_GAP",
                    node_id,
                    f"Rule {rule_id} requires at least {min_count} {direction} {edge_type} "
                    f"edge(s) to {related_type}; found {matches}",
                )

    view_ids: set[str] = set()
    for index, raw_view in enumerate(generated_views):
        if not isinstance(raw_view, dict):
            raise ValueError(f"generated_views[{index}] must be an object")
        context = f"generated_views[{index}]"
        view_id = require_text(raw_view, "id", context)
        expected = require_text(raw_view, "expected_fingerprint", context)
        actual = require_text(raw_view, "actual_fingerprint", context)
        if view_id in view_ids:
            finding("major", "DUPLICATE_VIEW_ID", view_id, "Generated-view ID is not unique")
        view_ids.add(view_id)
        if expected != actual:
            finding(
                "major",
                "STALE_GENERATED_VIEW",
                view_id,
                "Generated-view fingerprint does not match canonical input fingerprint",
            )

    raw_findings.sort(
        key=lambda item: (
            SEVERITY_ORDER[item["severity"]],
            item["code"],
            item["subject"],
            item["detail"],
        )
    )
    findings = [
        {"finding_id": f"TRC-{index:03d}", **item}
        for index, item in enumerate(raw_findings, start=1)
    ]
    if any(item["severity"] in {"critical", "major"} for item in findings):
        status = "FAIL"
    elif findings:
        status = "PASS_WITH_LIMITATIONS"
    else:
        status = "PASS"
    return {
        "status": status,
        "nodes": len(nodes),
        "edges": len(edges),
        "lifecycle_rules": len(lifecycle_rules),
        "generated_views": len(generated_views),
        "findings": findings,
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Traceability graph audit",
        "",
        f"Status: **{result['status']}**  ",
        f"Nodes: {result['nodes']}  ",
        f"Edges: {result['edges']}  ",
        f"Findings: {len(result['findings'])}",
        "",
    ]
    for item in result["findings"]:
        lines.append(
            f"- **{item['severity'].upper()} {item['finding_id']} {item['code']}** "
            f"`{item['subject']}`: {item['detail']}"
        )
    if not result["findings"]:
        lines.append("No structural traceability findings.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", type=Path)
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args()
    try:
        payload = json.loads(args.graph.read_text(encoding="utf-8"))
        result = audit(payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"graph contract error: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(render_markdown(result))
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
