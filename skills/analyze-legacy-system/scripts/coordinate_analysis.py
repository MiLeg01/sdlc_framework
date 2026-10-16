#!/usr/bin/env python3
"""Plan, checkpoint, and validate complete inventory-backed legacy analysis."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))
from plan_parallel_execution import PlanError, plan_execution  # noqa: E402


FINAL_COVERAGE_STATUSES = {
    "ANALYZED",
    "COVERED-BY-PARENT",
    "NON-EXECUTABLE-SUPPORT",
    "DUPLICATE-VARIANT",
    "OUT-OF-SCOPE",
    "SKIPPED-WITH-REASON",
    "BLOCKED",
}
ACTIVE_COVERAGE_STATUSES = {"PENDING"}
ALL_COVERAGE_STATUSES = FINAL_COVERAGE_STATUSES | ACTIVE_COVERAGE_STATUSES
REQUIRED_REASON_STATUSES = {
    "NON-EXECUTABLE-SUPPORT",
    "DUPLICATE-VARIANT",
    "OUT-OF-SCOPE",
    "SKIPPED-WITH-REASON",
    "BLOCKED",
}
VALID_STAGE_STATUSES = {"PENDING", "VALIDATED", "NOT-REQUIRED", "BLOCKED"}
STAGE_ORDER = ["synthesis", "requirements", "specifications", "dashboard", "coverage_validation"]
DEPTH_STATUSES = {"PENDING", "DEEP_VERIFIED", "ANALYZED", "PARTIAL", "BLOCKED", "NOT_APPLICABLE"}
DIMENSION_STATUSES = {"VERIFIED", "NOT_APPLICABLE", "BLOCKED"}
DEPTH_DIMENSIONS = {
    "structure", "behavior", "data", "dependencies", "business_rules", "interfaces",
    "error_handling", "non_functional", "maintainability", "migration_significance",
}
SEMANTIC_COUNT_FIELDS = {
    "flows", "business_rules", "data_structures", "dependencies", "interfaces", "defect_candidates", "unknowns",
}
CROSS_LANGUAGE_CLASSIFICATIONS = {
    "EQUIVALENT", "PARTIALLY_EQUIVALENT", "DIVERGENT", "MISSING", "UNKNOWN",
}


class AnalysisStateError(ValueError):
    """The configured analysis state is invalid or incomplete."""


def _load(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AnalysisStateError(f"cannot load {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise AnalysisStateError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path | None, payload: dict[str, Any]) -> None:
    text = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(path)
    else:
        print(text, end="")


def _portable_path(value: object, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AnalysisStateError(f"{context} must be a non-empty path")
    normalized = value.replace("\\", "/").strip("/")
    parts = PurePosixPath(normalized).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise AnalysisStateError(f"{context} must be a safe relative path")
    return PurePosixPath(*parts).as_posix()


def _fingerprint(value: object) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _validate_inventory(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    if inventory.get("schema_version") != 1:
        raise AnalysisStateError("inventory schema_version must be 1")
    artifacts = inventory.get("artifacts")
    if not isinstance(artifacts, list):
        raise AnalysisStateError("inventory.artifacts must be an array")
    if inventory.get("failures"):
        raise AnalysisStateError("inventory contains access failures; complete scope cannot be proven")
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(artifacts):
        if not isinstance(raw, dict):
            raise AnalysisStateError(f"inventory.artifacts[{index}] must be an object")
        artifact_id = raw.get("id")
        if not isinstance(artifact_id, str) or not artifact_id:
            raise AnalysisStateError(f"inventory.artifacts[{index}].id is required")
        path = _portable_path(raw.get("path"), f"inventory.artifacts[{index}].path")
        if artifact_id in seen_ids or path in seen_paths:
            raise AnalysisStateError(f"duplicate inventory artifact: {artifact_id} / {path}")
        seen_ids.add(artifact_id)
        seen_paths.add(path)
        normalized.append({**raw, "id": artifact_id, "path": path})
    return sorted(normalized, key=lambda item: item["path"])


def _matches(path: str, selectors: list[str]) -> bool:
    if not selectors:
        return True
    lowered = path.casefold()
    for raw in selectors:
        selector = raw.replace("\\", "/").strip().strip("/").casefold()
        if not selector:
            continue
        if any(character in selector for character in "*?["):
            if fnmatch.fnmatchcase(lowered, selector):
                return True
        elif lowered == selector or lowered.startswith(selector + "/") or selector in lowered:
            return True
    return False


def _logical_component(path: str) -> str:
    parts = PurePosixPath(path).parts
    if not parts:
        return "root"
    if parts[0].casefold() == "src" and len(parts) >= 4:
        return "/".join(parts[:4])
    return parts[0]


def _slice_key(artifact: dict[str, Any]) -> tuple[str, str]:
    language = str(artifact.get("language") or "unknown").casefold()
    kind = str(artifact.get("kind") or "other").casefold()
    path = str(artifact["path"])
    lowered = path.casefold()
    if language == "cobol":
        return "cobol", "COBOL programs"
    if language == "pli":
        return "pli", "PL/I programs"
    if language == "java":
        return "java-api", "Java/API implementation"
    if language in {"copybook", "pli-include"}:
        return "shared-data-definitions", "Copybooks and include data definitions"
    if language in {"xsd", "wsdl"} or language == "yaml" and any(token in lowered for token in ("/api/", "openapi", "swagger")):
        return "contracts", "API and integration contracts"
    if language in {"xml", "cics-csd"} or kind == "configuration":
        return "runtime-configuration", "Runtime and integration configuration"
    if kind == "build-descriptor" or language in {"groovy", "shell", "powershell"}:
        return "build-and-operations", "Build and operational definitions"
    if kind == "test":
        return "tests", "Tests and fixtures"
    if language == "markdown":
        return "documentation", "Authoritative project documentation"
    return "support", "Other eligible support artifacts"


def _context_ids(slice_key: str, groups: dict[str, list[dict[str, Any]]]) -> list[str]:
    dependencies = {
        "cobol": ["shared-data-definitions", "contracts", "runtime-configuration"],
        "pli": ["shared-data-definitions", "contracts", "runtime-configuration"],
        "java-api": ["contracts", "runtime-configuration", "build-and-operations"],
        "contracts": ["shared-data-definitions", "runtime-configuration"],
        "runtime-configuration": ["contracts", "build-and-operations"],
        "tests": ["contracts", "runtime-configuration"],
        "documentation": ["contracts"],
    }
    result: list[str] = []
    for dependency in dependencies.get(slice_key, []):
        items = groups.get(dependency, [])
        if dependency == "shared-data-definitions" and slice_key == "cobol":
            items = [item for item in items if item.get("language") == "copybook"]
        elif dependency == "shared-data-definitions" and slice_key == "pli":
            items = [item for item in items if item.get("language") == "pli-include"]
        result.extend(str(item["id"]) for item in items)
    return sorted(set(result))


def _previous_artifacts(checkpoint: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not checkpoint:
        return {}
    artifacts = checkpoint.get("coverage", {}).get("artifacts", [])
    if not isinstance(artifacts, list):
        raise AnalysisStateError("checkpoint.coverage.artifacts must be an array")
    return {str(item.get("artifact_id")): item for item in artifacts if isinstance(item, dict)}


def _coverage_record(
    artifact: dict[str, Any],
    mode: str,
    selectors: list[str],
    checkpoint_record: dict[str, Any] | None,
    slice_id: str | None,
) -> dict[str, Any]:
    relevant = artifact.get("disposition") == "eligible"
    selected = relevant and (mode != "BOUNDED" or _matches(str(artifact["path"]), selectors))
    status = "PENDING"
    reason = None
    if not relevant:
        status = "OUT-OF-SCOPE"
        reason = f"inventory disposition: {artifact.get('disposition', 'unknown')}"
    elif not selected:
        status = "OUT-OF-SCOPE"
        reason = "outside the explicit bounded analysis selector"
    elif checkpoint_record:
        same_hash = checkpoint_record.get("source_hash") == artifact.get("sha256")
        previous_status = checkpoint_record.get("status")
        if same_hash and previous_status in FINAL_COVERAGE_STATUSES:
            status = str(previous_status)
            reason = checkpoint_record.get("reason")
    depth_status = "PENDING" if selected else "NOT_APPLICABLE"
    if checkpoint_record and status != "PENDING":
        depth_status = str(checkpoint_record.get("depth_status") or "PARTIAL")
    return {
        "artifact_id": artifact["id"],
        "source_path": artifact["path"],
        "source_hash": artifact.get("sha256"),
        "kind": artifact.get("kind"),
        "language_type": artifact.get("language"),
        "logical_component": _logical_component(str(artifact["path"])),
        "assigned_slice": slice_id if selected else None,
        "status": status,
        "evidence_ids": list(checkpoint_record.get("evidence_ids", [])) if checkpoint_record and status != "PENDING" else [],
        "related_requirements": list(checkpoint_record.get("related_requirements", [])) if checkpoint_record and status != "PENDING" else [],
        "depth_status": depth_status,
        "depth_dimensions": dict(checkpoint_record.get("depth_dimensions", {})) if checkpoint_record and status != "PENDING" else {},
        "semantic_counts": dict(checkpoint_record.get("semantic_counts", {})) if checkpoint_record and status != "PENDING" else {},
        "complexity": list(checkpoint_record.get("complexity", [])) if checkpoint_record and status != "PENDING" else [],
        "reason": reason,
    }


def _coverage_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(str(item["status"]) for item in records)
    relevant = [item for item in records if item["status"] != "OUT-OF-SCOPE" or item["assigned_slice"]]
    unaccounted = [item["artifact_id"] for item in relevant if item["status"] in ACTIVE_COVERAGE_STATUSES]
    blocked = [item["artifact_id"] for item in relevant if item["status"] == "BLOCKED"]
    depth_counts = Counter(str(item.get("depth_status") or "PARTIAL") for item in relevant)
    depth_blocking = [
        item["artifact_id"] for item in relevant
        if item["status"] == "ANALYZED" and not _depth_complete(item)
    ]
    return {
        "discovered": len(records),
        "relevant": len(relevant),
        "accounted": len(relevant) - len(unaccounted),
        "unaccounted": len(unaccounted),
        "blocked": len(blocked),
        "by_status": dict(sorted(counts.items())),
        "unaccounted_artifact_ids": sorted(unaccounted),
        "blocked_artifact_ids": sorted(blocked),
        "depth": {
            "deep_verified": depth_counts["DEEP_VERIFIED"],
            "analyzed": depth_counts["ANALYZED"],
            "partial": depth_counts["PARTIAL"],
            "blocked": depth_counts["BLOCKED"],
            "not_applicable": depth_counts["NOT_APPLICABLE"],
            "blocking_artifact_ids": sorted(depth_blocking),
        },
    }


def _critical_executable(record: dict[str, Any]) -> bool:
    return str(record.get("kind", "")).casefold() == "source" and str(record.get("language_type", "")).casefold() in {
        "cobol", "pli", "java",
    }


def _depth_complete(record: dict[str, Any]) -> bool:
    status = record.get("status")
    depth = record.get("depth_status")
    if status == "ANALYZED":
        allowed = {"DEEP_VERIFIED"} if _critical_executable(record) else {"DEEP_VERIFIED", "ANALYZED"}
        if depth not in allowed:
            return False
        try:
            _validate_depth_update(record, dict(record))
        except AnalysisStateError:
            return False
        return True
    if status == "BLOCKED":
        return depth == "BLOCKED"
    if status in FINAL_COVERAGE_STATUSES:
        return depth in {"NOT_APPLICABLE", "DEEP_VERIFIED", "ANALYZED"}
    return False


def _validate_depth_update(record: dict[str, Any], update: dict[str, Any]) -> None:
    status = update.get("status")
    if status != "ANALYZED":
        expected = "BLOCKED" if status == "BLOCKED" else "NOT_APPLICABLE"
        if update.get("depth_status", expected) != expected:
            raise AnalysisStateError(
                f"artifact {record.get('artifact_id')} has invalid depth status for {status}: {update.get('depth_status')}"
            )
        update["depth_status"] = expected
        update.setdefault("depth_dimensions", {})
        update.setdefault("semantic_counts", {})
        update.setdefault("complexity", [])
        return
    depth_status = update.get("depth_status")
    allowed = {"DEEP_VERIFIED"} if _critical_executable(record) else {"DEEP_VERIFIED", "ANALYZED"}
    if depth_status not in allowed:
        raise AnalysisStateError(
            f"artifact {record.get('artifact_id')} depth status must be one of {sorted(allowed)}"
        )
    dimensions = update.get("depth_dimensions")
    if not isinstance(dimensions, dict):
        raise AnalysisStateError(f"artifact {record.get('artifact_id')} depth_dimensions must be an object")
    missing = sorted(DEPTH_DIMENSIONS - set(dimensions))
    if missing:
        raise AnalysisStateError(f"artifact {record.get('artifact_id')} depth dimensions are incomplete: {missing}")
    for name in sorted(DEPTH_DIMENSIONS):
        value = dimensions[name]
        if not isinstance(value, dict) or value.get("status") not in DIMENSION_STATUSES:
            raise AnalysisStateError(f"artifact {record.get('artifact_id')} depth dimension {name} is invalid")
        if value["status"] == "VERIFIED" and not value.get("evidence_ids"):
            raise AnalysisStateError(f"artifact {record.get('artifact_id')} depth dimension {name} lacks evidence")
        if value["status"] in {"NOT_APPLICABLE", "BLOCKED"} and not value.get("reason"):
            raise AnalysisStateError(f"artifact {record.get('artifact_id')} depth dimension {name} requires a reason")
        if depth_status == "DEEP_VERIFIED" and value["status"] == "BLOCKED":
            raise AnalysisStateError(f"artifact {record.get('artifact_id')} cannot be DEEP_VERIFIED with blocked dimension {name}")
    counts = update.get("semantic_counts")
    if not isinstance(counts, dict) or SEMANTIC_COUNT_FIELDS - set(counts):
        raise AnalysisStateError(f"artifact {record.get('artifact_id')} semantic_counts are incomplete")
    if any(not isinstance(counts[name], int) or isinstance(counts[name], bool) or counts[name] < 0 for name in SEMANTIC_COUNT_FIELDS):
        raise AnalysisStateError(f"artifact {record.get('artifact_id')} semantic_counts must be non-negative integers")
    if _critical_executable(record) and counts["flows"] < 1:
        raise AnalysisStateError(f"artifact {record.get('artifact_id')} deep executable analysis requires at least one flow")
    complexity = update.get("complexity")
    if not isinstance(complexity, list) or not complexity:
        raise AnalysisStateError(f"artifact {record.get('artifact_id')} deep analysis requires complexity evidence")
    for item in complexity:
        if not isinstance(item, dict) or not item.get("metric") or item.get("basis") not in {"MEASURED", "ASSESSED"} or "value" not in item:
            raise AnalysisStateError(f"artifact {record.get('artifact_id')} complexity entries require metric, MEASURED/ASSESSED basis, and value")


def _initial_lifecycle(requirements: str, specifications: str, dashboard: str) -> dict[str, dict[str, Any]]:
    return {
        "inventory": {"status": "VALIDATED", "required": True},
        "analysis_slices": {"status": "PENDING", "required": True},
        "synthesis": {"status": "PENDING", "required": True},
        "requirements": {"status": "NOT-REQUIRED" if requirements == "none" else "PENDING", "required": requirements != "none"},
        "specifications": {"status": "NOT-REQUIRED" if specifications == "none" else "PENDING", "required": specifications != "none"},
        "dashboard": {"status": "NOT-REQUIRED" if dashboard == "disabled" else "PENDING", "required": dashboard != "disabled"},
        "coverage_validation": {"status": "PENDING", "required": True},
    }


def _restore_lifecycle(
    checkpoint: dict[str, Any] | None,
    lifecycle: dict[str, dict[str, Any]],
    slices_validated: bool,
) -> None:
    if not checkpoint or not slices_validated:
        return
    previous = checkpoint.get("lifecycle", {})
    if not isinstance(previous, dict):
        return
    for stage in STAGE_ORDER:
        value = previous.get(stage)
        if isinstance(value, dict) and value.get("status") in {"VALIDATED", "BLOCKED"}:
            lifecycle[stage]["status"] = value["status"]
            if value.get("evidence_ids"):
                lifecycle[stage]["evidence_ids"] = list(value["evidence_ids"])


def _full_dag(slice_ids: list[str], lifecycle: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = [
        {"id": "inventory", "dependencies": [], "owner": "coordinator", "output": "analysis/source-inventory.json"}
    ]
    tasks.extend(
        {
            "id": slice_id,
            "dependencies": ["inventory"],
            "owner": "bounded-analysis-worker",
            "output": f"analysis/slices/{slice_id}.json",
        }
        for slice_id in slice_ids
    )
    previous = slice_ids or ["inventory"]
    tasks.append({"id": "synthesis", "dependencies": previous, "owner": "coordinator", "output": "analysis/system-synthesis.json"})
    previous = ["synthesis"]
    if lifecycle["requirements"]["required"]:
        tasks.append({"id": "requirements", "dependencies": previous, "owner": "requirements-synthesis", "output": "requirements/requirements.json"})
        previous = ["requirements"]
    if lifecycle["specifications"]["required"]:
        tasks.append({"id": "specifications", "dependencies": previous, "owner": "openspec-workflow", "output": "openspec/changes"})
        previous = ["specifications"]
    if lifecycle["dashboard"]["required"]:
        tasks.append({"id": "dashboard", "dependencies": previous, "owner": "dashboard-renderer", "output": "dashboard/index.html"})
        previous = ["dashboard"]
    tasks.append({"id": "coverage-validation", "dependencies": previous, "owner": "coordinator", "output": "analysis/coverage.json"})
    return tasks


def _pending_execution_plan(dag: list[dict[str, Any]], completed: set[str], max_concurrency: int) -> dict[str, Any]:
    pending = [task for task in dag if task["id"] not in completed]
    pending_ids = {task["id"] for task in pending}
    tasks = []
    for task in pending:
        output = str(task["output"])
        write_path = output if not output.endswith(".json") and not output.endswith(".html") else output
        tasks.append({
            "id": task["id"],
            "dependencies": sorted(set(task["dependencies"]) & pending_ids),
            "write_paths": [write_path],
            "shared_surfaces": [
                surface for surface in (
                    "canonical:requirements" if task["id"] == "requirements" else None,
                    "canonical:openspec" if task["id"] == "specifications" else None,
                    "generated:dashboard" if task["id"] == "dashboard" else None,
                    "canonical:coverage" if task["id"] == "coverage-validation" else None,
                ) if surface
            ],
        })
    if not tasks:
        return {"schema_version": 1, "max_concurrency": max_concurrency, "task_count": 0, "stage_count": 0, "parallel_stage_count": 0, "stages": [], "conflicts": []}
    try:
        return plan_execution({"schema_version": 1, "max_concurrency": max_concurrency, "tasks": tasks})
    except PlanError as exc:
        raise AnalysisStateError(str(exc)) from exc


def _completion(state: dict[str, Any]) -> dict[str, Any]:
    coverage = state["coverage"]["summary"]
    pending_stages = [
        stage for stage, value in state["lifecycle"].items()
        if value.get("required") and value.get("status") != "VALIDATED"
    ]
    blockers: list[str] = []
    if coverage["unaccounted"]:
        blockers.append(f"{coverage['unaccounted']} relevant artifacts are unaccounted")
    depth_blockers = coverage.get("depth", {}).get("blocking_artifact_ids", [])
    if depth_blockers:
        blockers.append(f"{len(depth_blockers)} analyzed artifacts have not passed the depth gate")
    blockers.extend(f"required stage is not validated: {stage}" for stage in pending_stages)
    return {
        "complete": not blockers,
        "status": "COMPLETE" if not blockers and not coverage["blocked"] else ("COMPLETE-WITH-BLOCKED-ITEMS" if not blockers else "INCOMPLETE"),
        "blockers": blockers,
        "blocked_artifact_ids": coverage["blocked_artifact_ids"],
    }


def plan_state(args: argparse.Namespace) -> dict[str, Any]:
    inventory = _load(args.inventory)
    artifacts = _validate_inventory(inventory)
    mode = args.mode.upper()
    selectors = [value for value in args.scope if value.strip()]
    checkpoint = _load(args.checkpoint) if args.checkpoint else None
    if mode == "FULL" and selectors:
        raise AnalysisStateError("FULL mode cannot accept bounded scope selectors")
    if mode == "BOUNDED" and not selectors:
        raise AnalysisStateError("BOUNDED mode requires at least one explicit scope selector")
    if mode == "CONTINUE":
        if checkpoint is None:
            raise AnalysisStateError("CONTINUE mode requires --checkpoint")
        target = str(checkpoint.get("target_mode") or checkpoint.get("mode") or "").upper()
        if target not in {"FULL", "BOUNDED"}:
            raise AnalysisStateError("checkpoint does not identify a FULL or BOUNDED target mode")
        selectors = list(checkpoint.get("scope", {}).get("selectors", []))
        mode_for_scope = target
    else:
        target = mode
        mode_for_scope = mode
    if args.max_concurrency < 1 or args.max_concurrency > 6:
        raise AnalysisStateError("max_concurrency must be between 1 and 6")

    selected_artifacts = [
        artifact for artifact in artifacts
        if artifact.get("disposition") == "eligible" and (mode_for_scope == "FULL" or _matches(str(artifact["path"]), selectors))
    ]
    groups: dict[str, list[dict[str, Any]]] = {}
    labels: dict[str, str] = {}
    for artifact in selected_artifacts:
        key, label = _slice_key(artifact)
        groups.setdefault(key, []).append(artifact)
        labels[key] = label
    slice_id_by_artifact = {
        str(artifact["id"]): f"slice-{key}"
        for key, items in groups.items() for artifact in items
    }
    previous_records = _previous_artifacts(checkpoint if mode == "CONTINUE" else None)
    records = [
        _coverage_record(
            artifact,
            mode_for_scope,
            selectors,
            previous_records.get(str(artifact["id"])),
            slice_id_by_artifact.get(str(artifact["id"])),
        )
        for artifact in artifacts
    ]
    coverage_by_id = {item["artifact_id"]: item for item in records}
    inventory_by_id = {str(item["id"]): item for item in artifacts}
    previous_slices = {
        str(item.get("id")): item for item in (checkpoint or {}).get("slices", []) if isinstance(item, dict)
    }
    slices: list[dict[str, Any]] = []
    for key in sorted(groups):
        primary_ids = sorted(str(item["id"]) for item in groups[key])
        context_ids = _context_ids(key, groups)
        input_ids = sorted(set(primary_ids) | set(context_ids))
        input_fingerprint = _fingerprint([
            {"id": artifact_id, "sha256": inventory_by_id[artifact_id].get("sha256")}
            for artifact_id in input_ids
        ])
        slice_id = f"slice-{key}"
        previous = previous_slices.get(slice_id, {})
        all_accounted = all(
            coverage_by_id[artifact_id]["status"] in FINAL_COVERAGE_STATUSES
            and _depth_complete(coverage_by_id[artifact_id])
            for artifact_id in primary_ids
        )
        validated = all_accounted and previous.get("status") == "VALIDATED" and previous.get("input_fingerprint") == input_fingerprint
        if previous.get("status") == "VALIDATED" and previous.get("input_fingerprint") != input_fingerprint:
            for artifact_id in primary_ids:
                coverage_by_id[artifact_id].update({
                    "status": "PENDING", "evidence_ids": [], "related_requirements": [],
                    "depth_status": "PENDING", "depth_dimensions": {}, "semantic_counts": {}, "complexity": [],
                    "reason": "slice input fingerprint changed",
                })
        slices.append({
            "id": slice_id,
            "domain": key,
            "label": labels[key],
            "status": "VALIDATED" if validated else "PENDING",
            "primary_artifact_ids": primary_ids,
            "context_artifact_ids": context_ids,
            "input_artifact_ids": input_ids,
            "input_fingerprint": input_fingerprint,
            "context_package": {
                "tool": "manage-project-memory",
                "request": {
                    "task": f"analyze-{key}",
                    "domains": [key],
                    "entities": [],
                    "dependency_depth": 1,
                    "max_records": max(20, min(120, len(input_ids) * 4)),
                },
                "mandatory": ["L0 project synopsis", "owned primary artifact IDs and hashes"],
                "useful": ["selected L1 domain summary", "related L2 entities", "unresolved questions", "evidence locations"],
                "irrelevant": ["unrelated domains", "full conversation", "complete project history"],
                "output_path": f"analysis/context/{slice_id}.json",
            },
            "output_path": f"analysis/slices/{slice_id}.json",
            "owner": "bounded-analysis-worker",
            "prohibited_writes": ["client_input", "requirements", "openspec", "dashboard", "analysis/coverage.json"],
        })

    lifecycle = _initial_lifecycle(args.requirements, args.specifications, args.dashboard)
    if slices and all(item["status"] == "VALIDATED" for item in slices):
        lifecycle["analysis_slices"]["status"] = "VALIDATED"
    _restore_lifecycle(checkpoint if mode == "CONTINUE" else None, lifecycle, lifecycle["analysis_slices"]["status"] == "VALIDATED")
    dag = _full_dag([item["id"] for item in slices], lifecycle)
    completed = {"inventory"}
    completed.update(item["id"] for item in slices if item["status"] == "VALIDATED")
    for stage in STAGE_ORDER:
        task_id = "coverage-validation" if stage == "coverage_validation" else stage
        if lifecycle[stage]["status"] in {"VALIDATED", "NOT-REQUIRED"}:
            completed.add(task_id)
    state: dict[str, Any] = {
        "schema_version": 1,
        "mode": mode,
        "target_mode": target,
        "scope": {
            "inventory_root": inventory.get("root", "."),
            "selectors": selectors,
            "protected_source": True,
        },
        "inventory": {
            "path": args.inventory.as_posix(),
            "fingerprint": inventory.get("fingerprint"),
            "discovered_count": len(artifacts),
            "eligible_count": sum(item.get("disposition") == "eligible" for item in artifacts),
        },
        "coverage": {"artifacts": records, "summary": _coverage_summary(records)},
        "slices": slices,
        "lifecycle": lifecycle,
        "dag": dag,
        "execution_plan": _pending_execution_plan(dag, completed, args.max_concurrency),
        "ownership": {
            "analysis_workers": "analysis/slices/<slice-id>.json only",
            "requirements_synthesis": "requirements canonical registry",
            "openspec_workflow": "OpenSpec specifications",
            "dashboard_renderer": "dashboard/ and no analysis worker",
            "coordinator": "coverage, synthesis, integration, progress, and completion",
        },
        "analysis_profile": {
            "scope_default": "FULL",
            "depth_default": "DEEP",
            "completion_gate": ["COVERAGE", "DEPTH"],
            "languages": sorted({
                str(item.get("language")).casefold()
                for item in selected_artifacts
                if str(item.get("language")).casefold() in {"cobol", "pli", "java"}
            }),
        },
    }
    state["analysis_profile"]["cross_language_required"] = len(state["analysis_profile"]["languages"]) > 1
    state["completion"] = _completion(state)
    state["fingerprint"] = _fingerprint({key: state[key] for key in ("schema_version", "target_mode", "scope", "inventory", "coverage", "slices", "lifecycle", "dag", "analysis_profile")})
    return state


def _validate_coverage_record(record: dict[str, Any]) -> None:
    status = record.get("status")
    if status not in ALL_COVERAGE_STATUSES:
        raise AnalysisStateError(f"artifact {record.get('artifact_id')} has invalid coverage status: {status}")
    if status in REQUIRED_REASON_STATUSES and not record.get("reason"):
        raise AnalysisStateError(f"artifact {record.get('artifact_id')} requires a reason for {status}")
    if status == "ANALYZED" and not record.get("evidence_ids"):
        raise AnalysisStateError(f"artifact {record.get('artifact_id')} is ANALYZED without evidence_ids")
    if record.get("depth_status") not in DEPTH_STATUSES:
        raise AnalysisStateError(f"artifact {record.get('artifact_id')} has invalid depth status: {record.get('depth_status')}")


def recompute(state: dict[str, Any]) -> None:
    artifacts = state.get("coverage", {}).get("artifacts", [])
    if not isinstance(artifacts, list):
        raise AnalysisStateError("coverage.artifacts must be an array")
    for item in artifacts:
        if not isinstance(item, dict):
            raise AnalysisStateError("coverage artifacts must be objects")
        _validate_coverage_record(item)
    state["coverage"]["summary"] = _coverage_summary(artifacts)
    slices = state.get("slices", [])
    by_id = {item["artifact_id"]: item for item in artifacts}
    for slice_record in slices:
        owned = [by_id[artifact_id] for artifact_id in slice_record["primary_artifact_ids"]]
        if owned and all(item["status"] in FINAL_COVERAGE_STATUSES and _depth_complete(item) for item in owned):
            slice_record["status"] = "VALIDATED"
        else:
            slice_record["status"] = "PENDING"
    if slices and all(item.get("status") == "VALIDATED" for item in slices):
        state["lifecycle"]["analysis_slices"]["status"] = "VALIDATED"
    state["completion"] = _completion(state)
    state["fingerprint"] = _fingerprint({key: state[key] for key in ("schema_version", "target_mode", "scope", "inventory", "coverage", "slices", "lifecycle", "dag", "analysis_profile")})


def record_slice(args: argparse.Namespace) -> dict[str, Any]:
    state = _load(args.state)
    result = _load(args.result)
    slice_id = result.get("slice_id")
    slices = {item.get("id"): item for item in state.get("slices", []) if isinstance(item, dict)}
    if slice_id not in slices:
        raise AnalysisStateError(f"unknown slice_id: {slice_id}")
    target = slices[slice_id]
    if result.get("input_fingerprint") != target.get("input_fingerprint"):
        raise AnalysisStateError(f"slice {slice_id} input fingerprint is stale")
    validation = result.get("validation")
    if not isinstance(validation, dict) or validation.get("status") != "PASS":
        raise AnalysisStateError(f"slice {slice_id} must return validation.status PASS")
    returned = result.get("artifacts")
    if not isinstance(returned, list):
        raise AnalysisStateError("slice result artifacts must be an array")
    returned_by_id = {item.get("artifact_id"): item for item in returned if isinstance(item, dict)}
    expected = set(target["primary_artifact_ids"])
    if set(returned_by_id) != expected:
        missing = sorted(expected - set(returned_by_id))
        extra = sorted(set(returned_by_id) - expected)
        raise AnalysisStateError(f"slice {slice_id} artifact accounting differs; missing={missing}, extra={extra}")
    coverage_by_id = {item["artifact_id"]: item for item in state["coverage"]["artifacts"]}
    for artifact_id in sorted(expected):
        update = returned_by_id[artifact_id]
        status = update.get("status")
        if status not in FINAL_COVERAGE_STATUSES or status == "OUT-OF-SCOPE":
            raise AnalysisStateError(f"slice {slice_id} returned invalid final status for {artifact_id}: {status}")
        record = coverage_by_id[artifact_id]
        _validate_depth_update(record, update)
        record["status"] = status
        record["evidence_ids"] = sorted(set(update.get("evidence_ids", [])))
        record["related_requirements"] = sorted(set(update.get("related_requirements", [])))
        record["depth_status"] = update["depth_status"]
        record["depth_dimensions"] = update["depth_dimensions"]
        record["semantic_counts"] = update["semantic_counts"]
        record["complexity"] = update["complexity"]
        record["reason"] = update.get("reason")
        _validate_coverage_record(record)
    target["worker_output"] = result.get("output_path")
    target["validation"] = validation
    recompute(state)
    return state


def advance_stage(args: argparse.Namespace) -> dict[str, Any]:
    state = _load(args.state)
    stage = args.stage
    lifecycle = state.get("lifecycle", {})
    if stage not in lifecycle or stage in {"inventory", "analysis_slices"}:
        raise AnalysisStateError(f"stage cannot be advanced directly: {stage}")
    if args.status not in {"VALIDATED", "BLOCKED"}:
        raise AnalysisStateError("stage status must be VALIDATED or BLOCKED")
    dependencies = {
        "synthesis": ["analysis_slices"],
        "requirements": ["synthesis"],
        "specifications": ["requirements"],
        "dashboard": ["specifications" if lifecycle.get("specifications", {}).get("required") else ("requirements" if lifecycle.get("requirements", {}).get("required") else "synthesis")],
        "coverage_validation": ["dashboard" if lifecycle.get("dashboard", {}).get("required") else ("specifications" if lifecycle.get("specifications", {}).get("required") else ("requirements" if lifecycle.get("requirements", {}).get("required") else "synthesis"))],
    }
    for dependency in dependencies[stage]:
        value = lifecycle[dependency]
        if value.get("required") and value.get("status") != "VALIDATED":
            raise AnalysisStateError(f"cannot advance {stage}; dependency {dependency} is not validated")
    if stage == "coverage_validation" and state["coverage"]["summary"]["unaccounted"]:
        raise AnalysisStateError("coverage validation cannot pass while relevant artifacts are unaccounted")
    if stage == "synthesis" and args.status == "VALIDATED" and state.get("analysis_profile", {}).get("cross_language_required"):
        stage_result_path = getattr(args, "stage_result", None)
        if not stage_result_path:
            raise AnalysisStateError("mixed-language synthesis VALIDATED requires a cross-language stage result")
        stage_result = _load(stage_result_path)
        comparison = stage_result.get("cross_language_comparison")
        if stage_result.get("status") != "PASS" or not isinstance(comparison, dict) or comparison.get("status") != "VALIDATED":
            raise AnalysisStateError("cross-language synthesis result is not VALIDATED")
        required_languages = set(state["analysis_profile"]["languages"])
        result_languages = {str(value).casefold() for value in comparison.get("languages", [])}
        if not required_languages <= result_languages:
            raise AnalysisStateError(
                f"cross-language synthesis omits languages: {sorted(required_languages - result_languages)}"
            )
        classifications = comparison.get("classifications")
        if not isinstance(classifications, dict) or set(classifications) != CROSS_LANGUAGE_CLASSIFICATIONS:
            raise AnalysisStateError("cross-language synthesis must report every equivalence classification")
        if any(not isinstance(classifications[name], int) or isinstance(classifications[name], bool) or classifications[name] < 0 for name in CROSS_LANGUAGE_CLASSIFICATIONS):
            raise AnalysisStateError("cross-language synthesis classification counts must be non-negative integers")
        if not comparison.get("evidence_ids"):
            raise AnalysisStateError("cross-language synthesis requires evidence IDs")
        unknowns = stage_result.get("unknowns")
        defects = stage_result.get("defect_candidates")
        if not isinstance(unknowns, list) or not isinstance(defects, list):
            raise AnalysisStateError("cross-language synthesis requires unknowns and defect_candidates registers")
        for item in defects:
            if not isinstance(item, dict) or item.get("decision") not in {"PRESERVE", "FIX", "DECISION_REQUIRED"} or not item.get("evidence_ids"):
                raise AnalysisStateError("defect candidates require PRESERVE/FIX/DECISION_REQUIRED and evidence IDs")
        lifecycle[stage]["stage_result"] = str(stage_result_path)
        lifecycle[stage]["cross_language_comparison"] = comparison
        lifecycle[stage]["unknown_count"] = len(unknowns)
        lifecycle[stage]["defect_candidate_count"] = len(defects)
    if stage == "dashboard" and args.status == "VALIDATED":
        qa_result_path = getattr(args, "qa_result", None)
        if not qa_result_path:
            raise AnalysisStateError("dashboard VALIDATED requires an independent lifecycle-QA result")
        qa_result = _load(qa_result_path)
        if qa_result.get("status") != "PASS" or qa_result.get("lifecycle_status") != "VALIDATED":
            raise AnalysisStateError("dashboard lifecycle QA is not VALIDATED")
        fingerprints = qa_result.get("fingerprints")
        if not isinstance(fingerprints, dict) or any(
            not fingerprints.get(name) for name in ("html", "design", "data")
        ):
            raise AnalysisStateError("dashboard lifecycle QA lacks matching HTML, design, or data fingerprints")
        lifecycle[stage]["qa_result"] = str(qa_result_path)
        lifecycle[stage]["qa_fingerprints"] = fingerprints
    lifecycle[stage]["status"] = args.status
    lifecycle[stage]["evidence_ids"] = sorted(set(args.evidence_id))
    lifecycle[stage]["reason"] = args.reason or None
    recompute(state)
    return state


def validate_complete(state: dict[str, Any]) -> dict[str, Any]:
    if state.get("schema_version") != 1:
        raise AnalysisStateError("analysis state schema_version must be 1")
    recompute(state)
    completion = state["completion"]
    if not completion["complete"]:
        raise AnalysisStateError("; ".join(completion["blockers"]))
    return {
        "status": "PASS_WITH_BLOCKED" if completion["blocked_artifact_ids"] else "PASS",
        "target_mode": state.get("target_mode"),
        "coverage": state["coverage"]["summary"],
        "depth": state["coverage"]["summary"].get("depth", {}),
        "slices": {"validated": sum(item.get("status") == "VALIDATED" for item in state["slices"]), "total": len(state["slices"])},
        "blocked_artifact_ids": completion["blocked_artifact_ids"],
        "fingerprint": state["fingerprint"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan = subparsers.add_parser("plan", help="create or resume the complete analysis plan")
    plan.add_argument("--inventory", required=True, type=Path)
    plan.add_argument("--output", type=Path)
    plan.add_argument("--mode", choices=["full", "bounded", "continue"], default="full")
    plan.add_argument("--scope", action="append", default=[], help="explicit bounded selector; repeatable")
    plan.add_argument("--checkpoint", type=Path)
    plan.add_argument("--requirements", choices=["required", "optional", "none"], default="required")
    plan.add_argument("--specifications", choices=["openspec", "none"], default="none")
    plan.add_argument("--dashboard", choices=["enabled", "disabled"], default="enabled")
    plan.add_argument("--max-concurrency", type=int, default=4)

    record = subparsers.add_parser("record", help="integrate one validated isolated slice result")
    record.add_argument("--state", required=True, type=Path)
    record.add_argument("--result", required=True, type=Path)
    record.add_argument("--output", type=Path)

    stage = subparsers.add_parser("stage", help="record a coordinator-owned fan-in stage")
    stage.add_argument("--state", required=True, type=Path)
    stage.add_argument("--stage", required=True, choices=STAGE_ORDER)
    stage.add_argument("--status", required=True, choices=["VALIDATED", "BLOCKED"])
    stage.add_argument("--evidence-id", action="append", default=[])
    stage.add_argument("--reason")
    stage.add_argument("--qa-result", type=Path, help="required independent lifecycle-QA result for dashboard VALIDATED")
    stage.add_argument("--stage-result", type=Path, help="structured fan-in result required by selected lifecycle stages")
    stage.add_argument("--output", type=Path)

    validate = subparsers.add_parser("validate", help="enforce the full completion gate")
    validate.add_argument("--state", required=True, type=Path)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "plan":
            payload = plan_state(args)
            _write(args.output, payload)
        elif args.command == "record":
            payload = record_slice(args)
            _write(args.output, payload)
        elif args.command == "stage":
            payload = advance_stage(args)
            _write(args.output, payload)
        else:
            payload = validate_complete(_load(args.state))
            print(json.dumps(payload, indent=2, sort_keys=True))
    except AnalysisStateError as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
