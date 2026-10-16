#!/usr/bin/env python3
"""Resolve the next Agent Commons lifecycle action from canonical project state."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


COLLECTIONS = {
    "requirement": "requirements",
    "specification": "specifications",
    "acceptance-criterion": "acceptance_criteria",
    "implementation-item": "implementation_items",
    "test": "tests",
    "evidence": "evidence",
}
TERMINAL_IMPLEMENTATION = {"implemented", "validated", "complete", "completed"}
PASS_VALIDATION = {"pass", "passed", "validated", "complete", "completed"}
READY = {"ready", "approved", "implementation-ready", "ready-for-implementation"}


class ContinuationError(ValueError):
    """Raised when canonical project state cannot be resolved safely."""


def _norm(value: object) -> str:
    return str(value or "").strip().lower().replace("_", "-")


def action(
    capability: str | None,
    *,
    subject: str | None = None,
    label: str,
    reason: str,
    required: bool = True,
    status: str = "ready",
    choices: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": status,
        "required": required,
        "capability": capability,
        "subject": subject,
        "label": label,
        "reason": reason,
    }
    result["command"] = f"${capability}{f' {subject}' if subject else ''}" if capability else None
    if choices:
        result["choices"] = choices
    return result


def describe_capability_resolution(
    manifest: dict[str, Any],
    next_action: dict[str, Any],
) -> dict[str, Any]:
    """Describe how a returned stable capability ID must be resolved by the runtime."""
    stable_id = next_action.get("capability")
    configured = manifest.get("selected_skills", [])
    selected_skills = configured if isinstance(configured, list) else []
    return {
        "stable_id": stable_id,
        "selected_in_manifest": stable_id in selected_skills if stable_id else None,
        "source": "canonical-agent-commons" if stable_id else None,
        "automatic_execution": False,
    }


def _manifest_section(text: str, name: str) -> str:
    match = re.search(rf"(?m)^{re.escape(name)}:\s*$\n(?P<body>(?:^  .*\n?)*)", text)
    return match.group("body") if match else ""


def _scalar(section: str, key: str) -> str:
    match = re.search(rf"(?m)^  {re.escape(key)}:\s*(.*?)\s*$", section)
    if not match:
        return ""
    value = match.group(1).strip().strip("'\"")
    return "" if value in {"", "null", "~"} else value


def _boolean(section: str, key: str) -> bool:
    return _norm(_scalar(section, key)) == "true"


def _list(section: str, key: str) -> list[str]:
    match = re.search(
        rf"(?m)^  {re.escape(key)}:\s*$\n(?P<body>(?:^    -\s+.*\n?)*)",
        section,
    )
    if not match:
        return []
    return [value.strip().strip("'\"") for value in re.findall(r"(?m)^    -\s+(.*?)\s*$", match.group("body"))]


def load_manifest(root: Path) -> dict[str, Any]:
    path = root / ".agent-commons.yaml"
    if not path.is_file():
        raise ContinuationError(f"missing project manifest: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    project = _manifest_section(text, "project")
    requirements = _manifest_section(text, "requirements")
    specifications = _manifest_section(text, "specifications")
    implementation = _manifest_section(text, "implementation")
    source_inventory = _manifest_section(text, "source_inventory")
    capability_state = _manifest_section(text, "capability_state")
    dashboard = _manifest_section(text, "dashboard")
    project_memory = _manifest_section(text, "project_memory")
    commons = _manifest_section(text, "commons")
    return {
        "path": str(path),
        "scopes": _list(project, "scopes"),
        "requirements_required": _boolean(requirements, "extraction"),
        "specification_method": _scalar(specifications, "method"),
        "specifications_required": _boolean(specifications, "generate_from_requirements"),
        "implementation_method": _scalar(implementation, "method"),
        "implementation_phase": _scalar(implementation, "phase"),
        "source_inventory_complete": _boolean(source_inventory, "complete"),
        "requires_user_choice": _boolean(capability_state, "requires_user_choice"),
        "dashboard_enabled": _boolean(dashboard, "enabled"),
        "project_memory_enabled": _boolean(project_memory, "enabled"),
        "project_memory_root": _scalar(project_memory, "root"),
        "selected_skills": _list(commons, "skills"),
    }


def load_state(root: Path, explicit: Path | None = None) -> tuple[dict[str, Any], str | None]:
    candidates = [explicit] if explicit else [
        root / "dashboard" / "data.json",
        root / "project-state.json",
        root / "analysis" / "project-state.json",
    ]
    for path in candidates:
        if path and path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ContinuationError(f"invalid project state JSON: {path}: {exc}") from exc
            if not isinstance(data, dict):
                raise ContinuationError(f"project state must be an object: {path}")
            return data, str(path)
    return {}, None


def load_memory_status(root: Path) -> dict[str, Any]:
    memory_root = root.expanduser().resolve() / ".agent-commons" / "memory"
    index_path = memory_root / "index.json"
    state_path = memory_root / "state.json"
    empty = {
        "available": False,
        "root": ".agent-commons/memory",
        "stale_record_ids": [],
        "conflicting_record_ids": [],
        "latest_checkpoint": None,
        "source_inventory_fingerprint": None,
        "next_action": None,
    }
    if not index_path.is_file() or not state_path.is_file():
        return empty
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContinuationError(f"invalid project memory JSON: {exc}") from exc
    if not isinstance(index, dict) or index.get("schema_version") != 1:
        raise ContinuationError("project memory index schema_version must be 1")
    if not isinstance(state, dict) or state.get("schema_version") != 1:
        raise ContinuationError("project memory state schema_version must be 1")
    records = index.get("records", [])
    checkpoints = index.get("checkpoints", [])
    if not isinstance(records, list) or not isinstance(checkpoints, list):
        raise ContinuationError("project memory index records and checkpoints must be arrays")
    project = state.get("project", {}) if isinstance(state.get("project"), dict) else {}
    return {
        "available": True,
        "root": str(index.get("storage_root") or ".agent-commons/memory"),
        "project_summary_path": index.get("project_summary_path"),
        "stale_record_ids": sorted(str(item.get("id")) for item in records if item.get("status") == "STALE"),
        "conflicting_record_ids": sorted(str(item.get("id")) for item in records if item.get("status") == "CONFLICTING"),
        "latest_checkpoint": str(checkpoints[-1].get("id")) if checkpoints else None,
        "source_inventory_fingerprint": index.get("source_inventory_fingerprint"),
        "next_action": project.get("next_action"),
    }


def _records(state: dict[str, Any]) -> dict[str, tuple[str, dict[str, Any]]]:
    records: dict[str, tuple[str, dict[str, Any]]] = {}
    for object_type, collection in COLLECTIONS.items():
        values = state.get(collection, [])
        if not isinstance(values, list):
            continue
        for item in values:
            if not isinstance(item, dict) or not str(item.get("id", "")).strip():
                continue
            identifier = str(item["id"]).strip()
            if identifier in records:
                raise ContinuationError(f"duplicate project object ID: {identifier}")
            records[identifier] = (object_type, item)
    return records


def _safe_project_path(root: Path, value: str) -> Path:
    root = root.expanduser().resolve()
    candidate = Path(value).expanduser()
    candidate = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ContinuationError(f"object path escapes the project root: {value}") from exc
    return candidate


def resolve_subject(root: Path, state: dict[str, Any], reference: str | None) -> tuple[str, dict[str, Any]] | None:
    if not reference:
        return None
    root = root.expanduser().resolve()
    records = _records(state)
    cleaned = reference.strip()
    prefixed = re.match(r"^(requirement|req|specification|spec)\s*[: ]\s*(.+)$", cleaned, re.I)
    if prefixed:
        cleaned = prefixed.group(2).strip()
    if cleaned in records:
        return records[cleaned]

    path_like = "/" in cleaned or cleaned.startswith((".", "~"))
    if path_like:
        candidate = _safe_project_path(root, cleaned)
        relative = candidate.relative_to(root).as_posix().rstrip("/")
        matches = []
        for object_type, item in records.values():
            locators = {
                str(item.get(key, "")).strip().rstrip("/")
                for key in ("path", "source", "source_path", "location", "dashboard_reference")
                if item.get(key)
            }
            if relative in locators or str(candidate) in locators:
                matches.append((object_type, item))
        if not matches and relative.startswith("openspec/changes/"):
            change = relative.split("/", 3)[2]
            matches = [
                record for record in records.values()
                if record[0] == "specification" and _norm(record[1].get("change") or record[1].get("slug")) == _norm(change)
            ]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise ContinuationError(f"object path is ambiguous: {reference}")
    raise ContinuationError(f"project object not found: {reference}")


def _relationships(state: dict[str, Any], relation_type: str, *, source: str | None = None, target: str | None = None) -> list[dict[str, Any]]:
    values = state.get("relationships", [])
    if not isinstance(values, list):
        return []
    return [
        item for item in values if isinstance(item, dict) and item.get("type") == relation_type
        and (source is None or item.get("source") == source)
        and (target is None or item.get("target") == target)
    ]


def _validation_status(specification: dict[str, Any]) -> str:
    return _norm(specification.get("validation_status") or specification.get("verification_status"))


def _dependency_ids(state: dict[str, Any], specification: dict[str, Any]) -> set[str]:
    identifier = str(specification["id"])
    return {
        *[str(relation.get("target")) for relation in _relationships(state, "depends-on", source=identifier)],
        *[str(value) for value in specification.get("dependency_ids", [])],
    }


def _spec_action(specification: dict[str, Any]) -> dict[str, Any]:
    identifier = str(specification["id"])
    status = _norm(specification.get("status"))
    readiness = _norm(specification.get("readiness"))
    implementation = _norm(specification.get("implementation_status"))
    validation = _validation_status(specification)
    if "blocked" in {status, readiness, implementation, validation}:
        return action(None, subject=identifier, label=f"Resolve blocker for {identifier}",
                      reason="The specification is blocked; implementation must not begin.", status="blocked")
    if readiness not in READY:
        return action("review-openspec-change", subject=identifier, label=f"Complete {identifier} readiness",
                      reason="The OpenSpec change is not yet approved and implementation-ready.")
    if implementation in TERMINAL_IMPLEMENTATION:
        if validation not in PASS_VALIDATION:
            return action("verify-openspec-implementation", subject=identifier, label=f"Validate {identifier}",
                          reason="Implementation is complete but specification verification is incomplete.")
        return action(None, subject=identifier, label=f"{identifier} is current",
                      reason="The specification is implemented and validated.", required=False, status="complete")
    return action("implement-openspec-change", subject=identifier, label=f"Implement {identifier}",
                  reason="The approved OpenSpec change is ready for TDD implementation.")


def _requirement_action(state: dict[str, Any], requirement: dict[str, Any]) -> dict[str, Any]:
    identifier = str(requirement["id"])
    status = _norm(requirement.get("status"))
    if status == "blocked" or requirement.get("unresolved_questions"):
        return action(None, subject=identifier, label=f"Resolve {identifier}",
                      reason="The requirement has an unresolved decision and is not implementation-ready.", status="blocked")
    if status not in {"approved", "specified", "ready", "implemented", "validated"}:
        return action("derive-modernization-requirements", subject=identifier, label=f"Refine {identifier}",
                      reason="The requirement must be evidence-backed and approved before specification or implementation.")
    records = _records(state)
    spec_ids = [str(item.get("target")) for item in _relationships(state, "specified-by", source=identifier)]
    spec_ids = list(dict.fromkeys([*spec_ids, *[str(value) for value in requirement.get("specification_ids", [])]]))
    specifications = [records[value][1] for value in spec_ids if value in records and records[value][0] == "specification"]
    if not specifications:
        return action("specify-openspec-change", subject=identifier, label=f"Specify {identifier}",
                      reason="No approved OpenSpec implementation contract is linked to this requirement.")
    pending = [item for item in specifications if _spec_action(item)["required"]]
    if len(pending) == 1:
        selected = _spec_action(pending[0])
        if selected["capability"] == "implement-openspec-change":
            return action("implement-ready-slice", subject=identifier, label=f"Implement {identifier}",
                          reason=f"The requirement resolves to ready specification {pending[0]['id']}; use TDD through the linked contract.")
        return selected
    if not pending:
        return action(None, subject=identifier, label=f"{identifier} is current",
                      reason="All linked specifications are implemented and validated.", required=False, status="complete")
    complete_ids = {
        str(item["id"]) for item in specifications
        if _norm(item.get("implementation_status")) in TERMINAL_IMPLEMENTATION
        and _validation_status(item) in PASS_VALIDATION
    }
    pending_ids = {str(item["id"]) for item in pending}
    eligible = [
        item for item in pending
        if all(dependency in complete_ids for dependency in _dependency_ids(state, item) - pending_ids)
        and not (_dependency_ids(state, item) & pending_ids)
    ]
    if len(eligible) == 1:
        selected = _spec_action(eligible[0])
        if selected["capability"] == "implement-openspec-change":
            return action("implement-ready-slice", subject=identifier, label=f"Implement {identifier}",
                          reason=f"Linked specification {eligible[0]['id']} is the unique dependency-ready next contract; use TDD through it.")
        return selected
    choices = [
        {"id": str(item["id"]), "command": str(_spec_action(item)["command"]), "reason": str(_spec_action(item)["reason"])}
        for item in pending
    ]
    return action(None, subject=identifier, label=f"Select the next specification for {identifier}",
                  reason="The requirement maps to multiple unfinished specifications and ordering is not unambiguous.",
                  status="choice-required", choices=choices)


def _ready_specs(state: dict[str, Any]) -> list[dict[str, Any]]:
    records = _records(state)
    specifications = [record for object_type, record in records.values() if object_type == "specification"]
    complete = {
        str(item["id"]) for item in specifications
        if _norm(item.get("implementation_status")) in TERMINAL_IMPLEMENTATION
        and _validation_status(item) in PASS_VALIDATION
    }
    result = []
    for item in specifications:
        if _spec_action(item)["capability"] != "implement-openspec-change":
            continue
        if all(value in complete for value in _dependency_ids(state, item)):
            result.append(item)
    return result


def apply_action_projection(manifest: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    """Attach derived project and object actions without introducing a second state store."""
    records = _records(state)
    for object_type, record in records.values():
        if object_type == "requirement":
            record["next_action"] = _requirement_action(state, record)
        elif object_type == "specification":
            record["next_action"] = _spec_action(record)
    project = state.setdefault("project", {})
    if not isinstance(project, dict):
        raise ContinuationError("project state must be an object")
    project["next_action"] = resolve_next_action(manifest, state)
    return state


def resolve_next_action(
    manifest: dict[str, Any],
    state: dict[str, Any],
    subject: tuple[str, dict[str, Any]] | None = None,
    *,
    memory_status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if manifest.get("requires_user_choice"):
        return action(None, label="Resolve initialization choice",
                      reason="A material capability or project decision is still unresolved.", status="blocked")
    if subject:
        object_type, record = subject
        if object_type == "requirement":
            return _requirement_action(state, record)
        if object_type == "specification":
            return _spec_action(record)
        return action(None, subject=str(record.get("id")), label="Inspect linked lifecycle object",
                      reason=f"{object_type} is contextual evidence; continue from its linked requirement or specification.",
                      status="choice-required")

    project = state.get("project", {}) if isinstance(state.get("project"), dict) else {}
    blockers = project.get("blockers", [])
    if blockers:
        return action(None, label="Resolve project blocker", reason=str(blockers[0]), status="blocked")

    legacy = "legacy-migration" in manifest.get("scopes", [])
    memory_status = memory_status or {}
    if legacy and memory_status.get("stale_record_ids"):
        return action(
            "analyze-legacy-system",
            label="Refresh stale legacy analysis",
            reason=(
                f"Project memory marks {len(memory_status['stale_record_ids'])} records stale after source change; "
                "reuse unchanged validated slices and reanalyze only affected dependencies."
            ),
        )
    if legacy and memory_status.get("conflicting_record_ids"):
        return action(
            "analyze-legacy-system",
            label="Reconcile conflicting legacy findings",
            reason=(
                f"Project memory preserves {len(memory_status['conflicting_record_ids'])} conflicting records; "
                "resume cross-system synthesis without overwriting either finding."
            ),
        )
    analysis = project.get("analysis", {}) if isinstance(project.get("analysis"), dict) else {}
    if not analysis and isinstance(state.get("analysis"), dict):
        analysis = state["analysis"]
    analysis_status = _norm(project.get("analysis_status") or analysis.get("status"))
    analysis_complete = analysis_status in {"complete", "complete-with-blocked-items", "completed", "current", "validated"}
    if legacy and (not manifest.get("source_inventory_complete") or not analysis_complete):
        return action("analyze-legacy-system", label="Analyze legacy source",
                      reason="The legacy evidence lifecycle has not completed; the analysis entry point owns inventory, bounded analysis, requirements, and selected downstream handoffs.")

    requirements = state.get("requirements", []) if isinstance(state.get("requirements"), list) else []
    requirements_required = bool(manifest.get("requirements_required"))
    if requirements_required and (not requirements or any(_norm(item.get("status")) in {"", "draft", "candidate", "incomplete"} for item in requirements if isinstance(item, dict))):
        return action("derive-modernization-requirements", label="Derive approved requirements",
                      reason="Analysis is available, but the required evidence-backed requirement set is missing or incomplete.")

    records = _records(state)
    specifications = [record for object_type, record in records.values() if object_type == "specification"]
    specifications_required = bool(manifest.get("specifications_required") or manifest.get("specification_method") == "openspec")
    approved_unlinked = []
    for requirement in requirements:
        if not isinstance(requirement, dict) or _norm(requirement.get("status")) != "approved":
            continue
        identifier = str(requirement.get("id", ""))
        if identifier and not _relationships(state, "specified-by", source=identifier) and not requirement.get("specification_ids"):
            approved_unlinked.append(identifier)
    if specifications_required and approved_unlinked:
        subject_id = approved_unlinked[0] if len(approved_unlinked) == 1 else None
        return action("specify-openspec-change", subject=subject_id, label="Create implementation specifications",
                      reason="Approved requirements exist without linked OpenSpec implementation contracts.")
    if specifications_required and not specifications:
        return action("specify-openspec-change", label="Create the first OpenSpec change",
                      reason="This project requires OpenSpec before implementation, but no specification exists.")

    unfinished = [item for item in specifications if _spec_action(item)["required"]]
    validation = [item for item in unfinished if _spec_action(item)["capability"] == "verify-openspec-implementation"]
    if validation:
        if len(validation) == 1:
            return _spec_action(validation[0])
        return action(None, label="Select a specification to validate",
                      reason="Several implemented specifications require verification.", status="choice-required",
                      choices=[{"id": str(item["id"]), "command": str(_spec_action(item)["command"]), "reason": str(_spec_action(item)["reason"])} for item in validation])

    ready = _ready_specs(state)
    if ready:
        if len(ready) == 1:
            return _spec_action(ready[0])
        priorities = [_norm(item.get("priority")) for item in ready]
        if priorities.count("critical") == 1:
            return _spec_action(ready[priorities.index("critical")])
        choices = [{"id": str(item["id"]), "command": str(_spec_action(item)["command"]), "reason": str(_spec_action(item)["reason"])} for item in ready]
        return action(None, label="Select the next ready specification",
                      reason="Multiple dependency-ready specifications exist and no unique priority determines the order.",
                      status="choice-required", choices=choices)

    reviews = [item for item in unfinished if _spec_action(item)["capability"] == "review-openspec-change"]
    if reviews:
        if len(reviews) == 1:
            return _spec_action(reviews[0])
        return action(None, label="Select a specification to complete",
                      reason="Multiple specifications have readiness gaps.", status="choice-required",
                      choices=[{"id": str(item["id"]), "command": str(_spec_action(item)["command"]), "reason": str(_spec_action(item)["reason"])} for item in reviews])

    return action(None, label="Project state is current",
                  reason="No required lifecycle continuation was found. Optional review, dashboard refresh, or planning actions may still be useful.",
                  required=False, status="complete")


def initial_next_action(
    *,
    scopes: list[str],
    requirements_required: bool,
    specification_method: str,
    specifications_required: bool,
    implementation_phase: str,
) -> dict[str, Any]:
    if "legacy-migration" in scopes:
        return action("analyze-legacy-system", label="Analyze legacy source",
                      reason="Begin the configured evidence-first analysis workflow; it will inventory first when needed and continue only through the selected project scope.")
    if specification_method == "openspec" or specifications_required:
        return action("specify-openspec-change", label="Create the first OpenSpec change",
                      reason="Implementation must begin from an approved specification and acceptance scenarios, not an unanchored coding task.")
    if implementation_phase == "active":
        return action("continue-project", label="Resolve the first approved delivery unit",
                      reason="Inspect the project state and choose an explicit requirement, specification, or approved slice before implementation.")
    if requirements_required:
        return action("derive-modernization-requirements", label="Derive approved requirements",
                      reason="The project requires an evidence-backed requirement set before downstream work.")
    return action("continue-project", label="Inspect the initialized project",
                  reason="Resolve the next lifecycle step from the project manifest and canonical state.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", nargs="?", help="stable ID or safe project-local path")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--state", type=Path, help="explicit structured project-state JSON")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"project root is not a directory: {root}")
    try:
        manifest = load_manifest(root)
        state, state_path = load_state(root, args.state.expanduser().resolve() if args.state else None)
        memory_status = load_memory_status(root)
        subject = resolve_subject(root, state, args.reference)
        next_action = resolve_next_action(manifest, state, subject, memory_status=memory_status)
        result = {
            "schema_version": 1,
            "project_root": ".",
            "manifest": ".agent-commons.yaml",
            "state_source": str(Path(state_path).resolve().relative_to(root)) if state_path else None,
            "resolved_subject": {"type": subject[0], "id": subject[1]["id"]} if subject else None,
            "memory": memory_status,
            "capability_resolution": describe_capability_resolution(manifest, next_action),
            "next_action": next_action,
        }
    except ContinuationError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
