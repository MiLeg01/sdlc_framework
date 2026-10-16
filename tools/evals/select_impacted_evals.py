#!/usr/bin/env python3
"""Select capability and workflow evaluations affected by repository changes."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import deque
from pathlib import Path
from typing import Any, Optional

from eval_common import (
    ROOT,
    EvalConfigError,
    capability_for_path,
    catalog_entries,
    impact_graph,
    load_capability_contracts,
    load_catalog,
    load_thresholds,
    load_workflows,
    normalize_repo_path,
    scenario_ids,
)


GLOBAL_GRAPH_PATHS = {
    "catalog/capabilities.yaml",
    "catalog/capability-index.json",
    "archetypes/composition.yaml",
    "evals/contracts/capabilities.json",
    "evals/contracts/agents.json",
    "evals/contracts/thresholds.json",
    "evals/mutations/hard-fail-cases.json",
    "evals/mutations/methodology-cases.json",
    "evals/fixtures/projects/index.json",
    "evals/workflows/contracts.json",
    "evals/schemas/eval-contract.schema.json",
    "evals/schemas/eval-result.schema.json",
    "evals/schemas/executor-input.schema.json",
    "evals/schemas/executor-output.schema.json",
    "evals/schemas/codex-executor-output.schema.json",
    "evals/schemas/judge-input.schema.json",
    "evals/schemas/judge-output.schema.json",
    "evals/schemas/last-green-baseline.schema.json",
    "evals/schemas/workflow-contract.schema.json",
}


def git_changed_files(base: str) -> list[str]:
    completed = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    committed = completed.stdout.splitlines()
    unstaged = subprocess.run(
        ["git", "diff", "--name-only"], cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    return sorted(set(committed + unstaged + staged + untracked))


def _archetype_membership(capabilities: set[str]) -> tuple[list[str], list[str]]:
    index_path = ROOT / "catalog" / "capability-index.json"
    data = json.loads(index_path.read_text(encoding="utf-8"))
    archetypes: set[str] = set()
    overlays: set[str] = set()
    for entry in data.get("capabilities", []):
        if entry.get("id") in capabilities:
            archetypes.update(entry.get("archetypes", []))
            overlays.update(entry.get("overlays", []))
    return sorted(archetypes), sorted(overlays)


def select_impacted(
    changed_files: list[str],
    changed_capability_ids: Optional[list[str]] = None,
) -> dict[str, Any]:
    normalized = sorted({normalize_repo_path(path) for path in changed_files})
    catalog = load_catalog()
    entries = catalog_entries(catalog)
    contracts = load_capability_contracts().get("capabilities", {})
    workflows = load_workflows().get("workflows", {})
    thresholds = load_thresholds()
    requested_capabilities = set(changed_capability_ids or [])
    unknown_requested = sorted(requested_capabilities - set(entries))
    if unknown_requested:
        raise EvalConfigError(f"unknown changed capability IDs: {unknown_requested}")
    protected_prefixes = tuple(thresholds.get("protected_paths", []))
    protected = sorted(
        path for path in normalized
        if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in protected_prefixes)
    )
    changed_archetypes = sorted({
        parts[1]
        for path in normalized
        for parts in [Path(path).parts]
        if len(parts) >= 3 and parts[0] == "archetypes" and parts[2] == "archetype.yaml"
    })
    changed_overlays = sorted({
        parts[2]
        for path in normalized
        for parts in [Path(path).parts]
        if len(parts) >= 4 and parts[0:2] == ("archetypes", "overlays") and parts[3] == "overlay.yaml"
    })

    all_capabilities = any(path in GLOBAL_GRAPH_PATHS for path in normalized)
    canonical_changed = {
        identifier
        for path in normalized
        for identifier in capability_for_path(path, entries)
    }
    for path in normalized:
        parts = Path(path).parts
        if len(parts) >= 2 and parts[0] == "skills" and parts[1] in entries:
            canonical_changed.add(parts[1])
    canonical_changed.update(requested_capabilities)
    uncovered_changed = sorted(canonical_changed - set(contracts))
    referenced_contracts = {
        identifier
        for identifier, contract in contracts.items()
        for scenario in contract.get("scenarios", [])
        for field in ("fixture", "golden")
        if str(scenario.get(field, "")).partition("#")[0] in normalized
    }
    referenced_workflows = {
        workflow_id
        for workflow_id, workflow in workflows.items()
        for scenario in workflow.get("scenarios", [])
        for field in ("fixture", "golden")
        if str(scenario.get(field, "")).partition("#")[0] in normalized
    }
    if all_capabilities:
        changed = set(contracts)
    else:
        changed = (canonical_changed & set(contracts)) | referenced_contracts
        for path in normalized:
            parts = Path(path).parts
            if len(parts) >= 2 and parts[0] == "skills" and parts[1] in contracts:
                changed.add(parts[1])
        if "tools/evals/eval_common.py" in normalized:
            changed.update({"run-evaluations", "select-impacted-evaluations"})
        if "evals/evaluation/test_impact_selector.py" in normalized:
            changed.add("select-impacted-evaluations")
        if any(path.startswith("evals/evaluation/test_") for path in normalized):
            changed.add("run-evaluations")
        if any(path.startswith("tools/evals/") for path in normalized):
            changed.add("run-evaluations")

    graph = impact_graph(catalog)
    direct = set()
    for identifier in changed:
        direct.update(graph.get(identifier, set()))
    direct &= set(contracts)
    direct -= changed

    critical = {
        identifier
        for identifier, contract in contracts.items()
        if contract.get("criticality") == "critical"
    }
    visited = set(changed) | set(direct)
    queue = deque((identifier, 1) for identifier in sorted(changed | direct))
    transitive: set[str] = set()
    while queue:
        identifier, depth = queue.popleft()
        if depth >= 3:
            continue
        for related in sorted(graph.get(identifier, set())):
            if related in visited:
                continue
            visited.add(related)
            queue.append((related, depth + 1))
            if related in critical:
                transitive.add(related)

    impacted = changed | direct | transitive
    workflow_ids = sorted(
        workflow_id
        for workflow_id, workflow in workflows.items()
        if (
            all_capabilities
            or workflow_id in referenced_workflows
            or canonical_changed.intersection(workflow.get("capabilities", []))
            or impacted.intersection(workflow.get("capabilities", []))
            or set(changed_archetypes).intersection(workflow.get("archetypes", []))
            or set(changed_overlays).intersection(workflow.get("overlays", []))
        )
    )
    archetypes, overlays = _archetype_membership(impacted)
    required_scenarios: list[str] = []
    for identifier in sorted(impacted):
        required_scenarios.extend(scenario_ids(identifier, contracts[identifier]))
    for workflow_id in workflow_ids:
        required_scenarios.extend(scenario_ids(workflow_id, workflows[workflow_id]))

    return {
        "schema_version": 1,
        "relationship_semantics": "catalog related links are symmetric evaluation-impact edges",
        "changed_files": normalized,
        "requested_capability_ids": sorted(requested_capabilities),
        "all_capabilities": all_capabilities,
        "changed_capabilities": sorted(changed),
        "uncovered_changed_capabilities": uncovered_changed,
        "changed_archetypes": changed_archetypes,
        "changed_overlays": changed_overlays,
        "direct_dependents": sorted(direct),
        "critical_transitive_dependents": sorted(transitive),
        "archetypes": archetypes,
        "overlays": overlays,
        "workflows": workflow_ids,
        "required_scenarios": sorted(set(required_scenarios)),
        "protected_changes": protected,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--capability", action="append", default=[], help="canonical changed capability ID")
    parser.add_argument("--changed-files-from", type=Path)
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--changed", action="store_true", help="discover changes from Git")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    changed = list(args.changed_file)
    if args.changed_files_from:
        changed.extend(args.changed_files_from.read_text(encoding="utf-8").splitlines())
    if args.changed or not (changed or args.capability):
        changed.extend(git_changed_files(args.base))
    try:
        result = select_impacted(changed, args.capability)
    except (EvalConfigError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"impact selection failed: {exc}", file=sys.stderr)
        return 2
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
