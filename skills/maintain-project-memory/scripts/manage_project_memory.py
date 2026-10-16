#!/usr/bin/env python3
"""Manage hierarchical evidence-backed Agent Commons project memory."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any, Iterator


MEMORY_ROOT = PurePosixPath(".agent-commons/memory")
CONFIDENCE = {"VERIFIED", "INFERRED", "UNKNOWN", "STALE", "CONFLICTING"}
LAYERS = {"L1", "L2"}
PROJECT_FIELDS = (
    "goal", "mode", "source_roots", "protected_paths", "target_technology", "languages",
    "architecture", "lifecycle_stage", "major_decisions", "critical_blockers", "next_action",
)


class ProjectMemoryError(ValueError):
    """Raised when project memory is invalid or cannot be updated safely."""


def _memory_dir(root: Path) -> Path:
    return root.expanduser().resolve() / MEMORY_ROOT


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _fingerprint(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def _atomic_json(path: Path, value: object) -> None:
    _atomic_text(path, json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProjectMemoryError(f"cannot load project memory file {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProjectMemoryError(f"project memory file must contain an object: {path}")
    return value


def _slug(value: object, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProjectMemoryError(f"{context} must be a non-empty string")
    result = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-.")
    if not result:
        raise ProjectMemoryError(f"{context} has no portable identifier")
    return result


def _safe_relative(root: Path, value: object, context: str) -> tuple[str, Path]:
    if not isinstance(value, str) or not value.strip():
        raise ProjectMemoryError(f"{context} must be a non-empty project-relative path")
    normalized = value.replace("\\", "/").strip().strip("/")
    parts = PurePosixPath(normalized).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ProjectMemoryError(f"{context} must be a safe project-relative path")
    relative = PurePosixPath(*parts).as_posix()
    project = root.expanduser().resolve()
    resolved = (project / relative).resolve()
    try:
        resolved.relative_to(project)
    except ValueError as exc:
        raise ProjectMemoryError(f"{context} escapes the project root: {value}") from exc
    return relative, resolved


@contextmanager
def _write_lock(memory: Path) -> Iterator[None]:
    memory.mkdir(parents=True, exist_ok=True)
    path = memory / ".write-lock"
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise ProjectMemoryError(f"project memory is locked for another writer: {path}") from exc
    try:
        os.write(descriptor, str(os.getpid()).encode("ascii"))
        os.close(descriptor)
        yield
    finally:
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def _project_summary(project: dict[str, Any]) -> str:
    def values(name: str) -> str:
        value = project.get(name)
        if isinstance(value, list):
            return ", ".join(str(item) for item in value) or "None"
        return str(value or "None")

    return "\n".join([
        "# Project synopsis", "",
        f"- Goal: {values('goal')}",
        f"- Mode: {values('mode')}",
        f"- Source roots: {values('source_roots')}",
        f"- Protected paths: {values('protected_paths')}",
        f"- Target technology: {values('target_technology')}",
        f"- Languages: {values('languages')}",
        f"- Architecture: {values('architecture')}",
        f"- Lifecycle stage: {values('lifecycle_stage')}",
        f"- Major decisions: {values('major_decisions')}",
        f"- Critical blockers: {values('critical_blockers')}",
        f"- Next action: {values('next_action')}", "",
    ])


def _validate_project(project: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(project, dict):
        raise ProjectMemoryError("project synopsis must be an object")
    missing = [field for field in PROJECT_FIELDS if field not in project]
    if missing:
        raise ProjectMemoryError(f"project synopsis is missing fields: {missing}")
    return {field: project[field] for field in PROJECT_FIELDS}


def _record_path(memory: Path, identifier: str) -> Path:
    return memory / "entities" / f"{_slug(identifier, 'record id')}.json"


def _domain_path(memory: Path, identifier: str) -> Path:
    return memory / "domains" / f"{_slug(identifier, 'domain id')}.json"


def _checkpoint_path(memory: Path, identifier: str) -> Path:
    return memory / "checkpoints" / f"{_slug(identifier, 'checkpoint id')}.json"


def _merge_unique(*values: object) -> list[Any]:
    result: list[Any] = []
    seen: set[str] = set()
    for value in values:
        for item in value if isinstance(value, list) else []:
            key = _canonical_json(item)
            if key not in seen:
                seen.add(key)
                result.append(item)
    return result


def _validate_record(root: Path, raw: object) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ProjectMemoryError("memory record must be an object")
    required = {"id", "layer", "domain", "entity", "statement", "confidence", "canonical_refs", "evidence", "relationships", "tags"}
    missing = sorted(required - raw.keys())
    if missing:
        raise ProjectMemoryError(f"memory record is missing fields: {missing}")
    identifier = _slug(raw["id"], "record id")
    if raw["layer"] not in LAYERS:
        raise ProjectMemoryError(f"record {identifier} has invalid layer: {raw['layer']}")
    if raw["confidence"] not in CONFIDENCE:
        raise ProjectMemoryError(f"record {identifier} has invalid confidence: {raw['confidence']}")
    if not isinstance(raw["entity"], dict) or not raw["entity"].get("id") or not raw["entity"].get("type"):
        raise ProjectMemoryError(f"record {identifier} requires entity.id and entity.type")
    if not isinstance(raw["statement"], str) or not raw["statement"].strip():
        raise ProjectMemoryError(f"record {identifier} requires a statement")
    record = {
        "schema_version": 1,
        "id": identifier,
        "layer": raw["layer"],
        "domain": _slug(raw["domain"], f"record {identifier} domain").casefold(),
        "entity": {"id": str(raw["entity"]["id"]), "type": str(raw["entity"]["type"])},
        "statement": raw["statement"].strip(),
        "confidence": raw["confidence"],
        "status": raw.get("status", "CURRENT"),
        "canonical_refs": list(raw["canonical_refs"]),
        "evidence": list(raw["evidence"]),
        "relationships": list(raw["relationships"]),
        "tags": sorted({str(value) for value in raw["tags"]}),
    }
    if "variants" in raw:
        record["variants"] = list(raw["variants"])
    for index, reference in enumerate(record["canonical_refs"]):
        if not isinstance(reference, dict) or "path" not in reference:
            raise ProjectMemoryError(f"record {identifier} canonical_refs[{index}] requires path")
        relative, _ = _safe_relative(root, reference["path"], f"record {identifier} canonical reference")
        reference["path"] = relative
    for index, evidence in enumerate(record["evidence"]):
        if not isinstance(evidence, dict) or "path" not in evidence:
            raise ProjectMemoryError(f"record {identifier} evidence[{index}] requires path")
        relative, _ = _safe_relative(root, evidence["path"], f"record {identifier} evidence")
        evidence["path"] = relative
        if "sha256" in evidence and not re.fullmatch(r"[0-9a-f]{64}", str(evidence["sha256"])):
            raise ProjectMemoryError(f"record {identifier} evidence[{index}].sha256 is invalid")
    for relationship in record["relationships"]:
        if not isinstance(relationship, dict) or not relationship.get("type") or not relationship.get("target"):
            raise ProjectMemoryError(f"record {identifier} relationship requires type and target")
    return record


def _semantic_identity(record: dict[str, Any]) -> str:
    return _fingerprint({
        key: record.get(key)
        for key in ("layer", "domain", "entity", "statement", "canonical_refs", "evidence", "relationships")
    })


def _merge_record(existing: dict[str, Any] | None, incoming: dict[str, Any]) -> dict[str, Any]:
    if existing is None:
        return incoming
    if existing.get("confidence") == "CONFLICTING":
        variants = list(existing.get("variants", []))
        if all(_semantic_identity(value) != _semantic_identity(incoming) for value in variants if isinstance(value, dict)):
            variants.append(incoming)
        existing["variants"] = variants
        existing["canonical_refs"] = _merge_unique(existing.get("canonical_refs"), incoming.get("canonical_refs"))
        existing["evidence"] = _merge_unique(existing.get("evidence"), incoming.get("evidence"))
        existing["relationships"] = _merge_unique(existing.get("relationships"), incoming.get("relationships"))
        existing["tags"] = sorted(set(existing.get("tags", [])) | set(incoming.get("tags", [])))
        return existing
    if _semantic_identity(existing) == _semantic_identity(incoming):
        incoming["canonical_refs"] = _merge_unique(existing.get("canonical_refs"), incoming.get("canonical_refs"))
        incoming["evidence"] = _merge_unique(existing.get("evidence"), incoming.get("evidence"))
        incoming["relationships"] = _merge_unique(existing.get("relationships"), incoming.get("relationships"))
        incoming["tags"] = sorted(set(existing.get("tags", [])) | set(incoming.get("tags", [])))
        return incoming
    return {
        "schema_version": 1,
        "id": incoming["id"],
        "layer": incoming["layer"],
        "domain": incoming["domain"],
        "entity": incoming["entity"],
        "statement": "Conflicting verified project-memory variants require synthesis.",
        "confidence": "CONFLICTING",
        "status": "CONFLICTING",
        "canonical_refs": _merge_unique(existing.get("canonical_refs"), incoming.get("canonical_refs")),
        "evidence": _merge_unique(existing.get("evidence"), incoming.get("evidence")),
        "relationships": _merge_unique(existing.get("relationships"), incoming.get("relationships")),
        "tags": sorted(set(existing.get("tags", [])) | set(incoming.get("tags", []))),
        "variants": [existing, incoming],
    }


def _relative(memory: Path, path: Path) -> str:
    return path.relative_to(memory.parent.parent).as_posix()


def _rebuild_index(root: Path) -> dict[str, Any]:
    memory = _memory_dir(root)
    state_path = memory / "state.json"
    if not state_path.is_file():
        raise ProjectMemoryError("project memory is not initialized")
    domains: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    checkpoints: list[dict[str, Any]] = []
    for path in sorted((memory / "domains").glob("*.json")):
        value = _load_json(path)
        domains.append({
            "id": value.get("id"), "path": _relative(memory, path),
            "record_ids": sorted(set(value.get("record_ids", []))), "sha256": _file_hash(path),
        })
    for path in sorted((memory / "entities").glob("*.json")):
        value = _load_json(path)
        records.append({
            "id": value.get("id"), "path": _relative(memory, path), "domain": value.get("domain"),
            "entity_id": value.get("entity", {}).get("id"), "confidence": value.get("confidence"),
            "status": value.get("status"), "sha256": _file_hash(path),
        })
    for path in sorted((memory / "checkpoints").glob("*.json")):
        value = _load_json(path)
        checkpoints.append({
            "id": value.get("id"), "path": _relative(memory, path), "status": value.get("status"),
            "sha256": _file_hash(path),
        })
    index = {
        "schema_version": 1,
        "storage_root": MEMORY_ROOT.as_posix(),
        "hierarchy": ["L0", "L1", "L2", "EVIDENCE"],
        "source_of_truth": "canonical project evidence and structured state",
        "state_path": _relative(memory, state_path),
        "project_summary_path": _relative(memory, memory / "project-summary.md"),
        "domains": domains,
        "records": records,
        "checkpoints": checkpoints,
        "decisions_path": _relative(memory, memory / "decisions.json"),
        "terminology_path": _relative(memory, memory / "terminology.json"),
        "source_state_path": _relative(memory, memory / "source-state.json") if (memory / "source-state.json").is_file() else None,
        "stale_record_count": sum(item["status"] == "STALE" for item in records),
        "conflicting_record_count": sum(item["status"] == "CONFLICTING" for item in records),
    }
    if index["source_state_path"]:
        source_state = _load_json(memory / "source-state.json")
        index["source_inventory_fingerprint"] = source_state.get("fingerprint")
    index["fingerprint"] = _fingerprint({key: index[key] for key in index if key != "fingerprint"})
    _atomic_json(memory / "index.json", index)
    return index


def initialize_memory(root: Path, project: dict[str, Any]) -> dict[str, Any]:
    project = _validate_project(project)
    memory = _memory_dir(root)
    with _write_lock(memory):
        for name in ("domains", "entities", "checkpoints"):
            (memory / name).mkdir(parents=True, exist_ok=True)
        state = {"schema_version": 1, "layer": "L0", "project": project}
        _atomic_json(memory / "state.json", state)
        _atomic_text(memory / "project-summary.md", _project_summary(project))
        for name in ("decisions.json", "terminology.json"):
            path = memory / name
            if not path.exists():
                _atomic_json(path, {"schema_version": 1, "records": []})
        index = _rebuild_index(root)
    return {"status": "INITIALIZED", "storage_root": index["storage_root"], "fingerprint": index["fingerprint"]}


def merge_proposal(root: Path, proposal: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(proposal, dict) or proposal.get("schema_version") != 1:
        raise ProjectMemoryError("memory proposal schema_version must be 1")
    producer = proposal.get("producer")
    if not isinstance(producer, dict) or producer.get("validation_status") != "PASS":
        raise ProjectMemoryError("memory proposal requires producer.validation_status PASS")
    memory = _memory_dir(root)
    if not (memory / "state.json").is_file():
        raise ProjectMemoryError("project memory is not initialized")
    domains = proposal.get("domains", [])
    records = proposal.get("records", [])
    if not isinstance(domains, list) or not isinstance(records, list):
        raise ProjectMemoryError("memory proposal domains and records must be arrays")
    normalized_records = [_validate_record(root, item) for item in records]
    conflict_count = 0
    with _write_lock(memory):
        for domain in domains:
            if not isinstance(domain, dict) or not domain.get("id") or not isinstance(domain.get("summary"), str):
                raise ProjectMemoryError("domain proposal requires id and summary")
            identifier = _slug(domain["id"], "domain id").casefold()
            path = _domain_path(memory, identifier)
            existing = _load_json(path) if path.is_file() else {"schema_version": 1, "id": identifier, "summary": "", "record_ids": []}
            existing["summary"] = domain["summary"].strip()
            _atomic_json(path, existing)
        for incoming in normalized_records:
            path = _record_path(memory, incoming["id"])
            existing = _load_json(path) if path.is_file() else None
            merged = _merge_record(existing, incoming)
            conflict_count += merged.get("confidence") == "CONFLICTING"
            _atomic_json(path, merged)
            domain_path = _domain_path(memory, incoming["domain"])
            domain = _load_json(domain_path) if domain_path.is_file() else {
                "schema_version": 1, "id": incoming["domain"], "summary": "", "record_ids": [],
            }
            domain["record_ids"] = sorted(set(domain.get("record_ids", [])) | {incoming["id"]})
            _atomic_json(domain_path, domain)
        checkpoint = proposal.get("checkpoint")
        if checkpoint is not None:
            if not isinstance(checkpoint, dict) or not checkpoint.get("id") or not checkpoint.get("status"):
                raise ProjectMemoryError("checkpoint proposal requires id and status")
            _atomic_json(_checkpoint_path(memory, checkpoint["id"]), {"schema_version": 1, **checkpoint})
        index = _rebuild_index(root)
    return {
        "status": "MERGED", "merged_records": len(normalized_records), "conflicting_records": conflict_count,
        "fingerprint": index["fingerprint"],
    }


def _all_records(root: Path, index: dict[str, Any]) -> dict[str, dict[str, Any]]:
    project = root.expanduser().resolve()
    return {str(item["id"]): _load_json(project / str(item["path"])) for item in index.get("records", [])}


def _memory_bytes(root: Path, index: dict[str, Any]) -> int:
    project = root.expanduser().resolve()
    paths = {
        index.get("state_path"), index.get("project_summary_path"), index.get("decisions_path"), index.get("terminology_path"),
        index.get("source_state_path"),
        *[item.get("path") for item in index.get("domains", [])],
        *[item.get("path") for item in index.get("records", [])],
        *[item.get("path") for item in index.get("checkpoints", [])],
    }
    return sum((project / str(path)).stat().st_size for path in paths if path and (project / str(path)).is_file())


def build_context_package(root: Path, request: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(request, dict) or not str(request.get("task", "")).strip():
        raise ProjectMemoryError("context request requires task")
    project_root = root.expanduser().resolve()
    memory = _memory_dir(root)
    index = _load_json(memory / "index.json")
    state = _load_json(memory / "state.json")
    records = _all_records(root, index)
    selected_domains = {_slug(value, "requested domain").casefold() for value in request.get("domains", [])}
    selected_entities = {str(value) for value in request.get("entities", [])}
    selected_ids = {
        identifier for identifier, record in records.items()
        if record.get("domain") in selected_domains or str(record.get("entity", {}).get("id")) in selected_entities
    }
    reverse_relationships: dict[str, set[str]] = {}
    for identifier, record in records.items():
        for relationship in record.get("relationships", []):
            if relationship.get("external"):
                continue
            reverse_relationships.setdefault(str(relationship.get("target", "")), set()).add(identifier)
    frontier = set(selected_ids)
    for _ in range(int(request.get("dependency_depth", 0))):
        next_frontier: set[str] = set()
        for identifier in frontier:
            for relationship in records[identifier].get("relationships", []):
                target = str(relationship.get("target", ""))
                if target in records and target not in selected_ids:
                    next_frontier.add(target)
            next_frontier.update(reverse_relationships.get(identifier, set()) - selected_ids)
        selected_ids.update(next_frontier)
        frontier = next_frontier
    max_records = int(request.get("max_records", 50))
    if max_records < 1:
        raise ProjectMemoryError("context request max_records must be positive")
    ordered_ids = sorted(selected_ids)
    included_ids = ordered_ids[:max_records]
    omitted_relevant = ordered_ids[max_records:]
    included_records = [records[identifier] for identifier in included_ids]
    included_domain_ids = sorted(set(selected_domains) | {str(record.get("domain")) for record in included_records})
    domains_by_id = {
        str(item["id"]): _load_json(project_root / str(item["path"])) for item in index.get("domains", [])
    }
    max_checkpoints = int(request.get("max_checkpoints", 3))
    if max_checkpoints < 0:
        raise ProjectMemoryError("context request max_checkpoints must be non-negative")
    checkpoint_values = [
        _load_json(project_root / str(item["path"])) for item in index.get("checkpoints", [])
    ]
    checkpoint_values.sort(key=lambda item: (int(item.get("order", 0)), str(item.get("id", ""))))
    selected_checkpoints = checkpoint_values[-max_checkpoints:] if max_checkpoints else []
    package: dict[str, Any] = {
        "schema_version": 1,
        "task": str(request["task"]),
        "selection": {
            "policy": "MINIMUM_SUFFICIENT_VERIFIED_CONTEXT",
            "mandatory": ["L0 project synopsis", *[f"L1 domain:{value}" for value in included_domain_ids]],
            "useful_record_ids": included_ids,
            "omitted_relevant_record_ids": omitted_relevant,
            "irrelevant_record_ids": sorted(set(records) - set(ordered_ids)),
        },
        "project": state["project"],
        "domains": [domains_by_id[value] for value in included_domain_ids if value in domains_by_id],
        "records": included_records,
        "checkpoints": selected_checkpoints,
        "stale_record_ids": sorted(identifier for identifier, record in records.items() if record.get("status") == "STALE"),
        "conflicting_record_ids": sorted(identifier for identifier, record in records.items() if record.get("status") == "CONFLICTING"),
    }
    package_bytes = len(_canonical_json(package).encode("utf-8"))
    package["metrics"] = {
        "package_bytes": package_bytes,
        "available_memory_bytes": _memory_bytes(root, index),
        "included_records": len(included_ids),
        "available_records": len(records),
        "included_checkpoints": len(selected_checkpoints),
        "available_checkpoints": len(checkpoint_values),
    }
    return package


def invalidate_memory(root: Path, inventory: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(inventory, dict) or inventory.get("schema_version") != 1:
        raise ProjectMemoryError("source inventory schema_version must be 1")
    artifacts = inventory.get("artifacts")
    if not isinstance(artifacts, list):
        raise ProjectMemoryError("source inventory artifacts must be an array")
    source_hashes: dict[str, str | None] = {}
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict) or "path" not in artifact:
            raise ProjectMemoryError(f"source inventory artifacts[{index}] requires path")
        path, _ = _safe_relative(root, artifact["path"], f"source inventory artifacts[{index}].path")
        source_hashes[path] = str(artifact.get("sha256")) if artifact.get("sha256") else None

    memory = _memory_dir(root)
    index = _load_json(memory / "index.json")
    records = _all_records(root, index)
    directly_stale: set[str] = set()
    dependency_stale: set[str] = set()
    reasons: dict[str, list[str]] = {}
    for identifier, record in records.items():
        if record.get("status") == "CONFLICTING":
            continue
        for evidence in record.get("evidence", []):
            path = str(evidence.get("path"))
            expected = evidence.get("sha256")
            if path in source_hashes and expected and source_hashes[path] != expected:
                directly_stale.add(identifier)
                reasons.setdefault(identifier, []).append(f"source hash changed: {path}")
            elif path not in source_hashes and expected:
                directly_stale.add(identifier)
                reasons.setdefault(identifier, []).append(f"source left the current inventory: {path}")

    stale_ids = set(directly_stale)
    changed = True
    while changed:
        changed = False
        for identifier, record in records.items():
            if identifier in stale_ids or record.get("status") == "CONFLICTING":
                continue
            targets = {
                str(relationship.get("target"))
                for relationship in record.get("relationships", [])
                if not relationship.get("external")
            }
            affected = sorted(targets & stale_ids)
            if affected:
                stale_ids.add(identifier)
                dependency_stale.add(identifier)
                reasons.setdefault(identifier, []).append(
                    "dependent memory changed: " + ", ".join(affected)
                )
                changed = True

    with _write_lock(memory):
        for identifier in sorted(stale_ids):
            record = records[identifier]
            if record.get("status") != "STALE":
                record["previous_confidence"] = record.get("confidence")
            record["confidence"] = "STALE"
            record["status"] = "STALE"
            record["invalidation_reasons"] = sorted(set(reasons.get(identifier, [])))
            _atomic_json(_record_path(memory, identifier), record)
        _atomic_json(memory / "source-state.json", {
            "schema_version": 1,
            "fingerprint": inventory.get("fingerprint"),
            "artifacts": [
                {"path": path, "sha256": source_hashes[path]} for path in sorted(source_hashes)
            ],
        })
        rebuilt = _rebuild_index(root)
    return {
        "status": "INVALIDATED" if stale_ids else "CURRENT",
        "directly_invalidated_record_ids": sorted(directly_stale),
        "dependency_invalidated_record_ids": sorted(dependency_stale),
        "current_record_ids": sorted(set(records) - stale_ids),
        "source_inventory_fingerprint": rebuilt.get("source_inventory_fingerprint"),
    }


def compact_memory(root: Path) -> dict[str, Any]:
    memory = _memory_dir(root)
    index = _load_json(memory / "index.json")
    records_before = len(index.get("records", []))
    bytes_before = _memory_bytes(root, index)
    with _write_lock(memory):
        state = _load_json(memory / "state.json")
        _atomic_text(memory / "project-summary.md", _project_summary(_validate_project(state.get("project", {}))))
        for path in sorted((memory / "domains").glob("*.json")):
            domain = _load_json(path)
            domain["record_ids"] = sorted(set(domain.get("record_ids", [])))
            _atomic_json(path, domain)
        rebuilt = _rebuild_index(root)
    return {
        "status": "COMPACTED",
        "preserved_records": records_before,
        "bytes_before": bytes_before,
        "bytes_after": _memory_bytes(root, rebuilt),
        "fingerprint": rebuilt.get("fingerprint"),
    }


def rebuild_memory(root: Path) -> dict[str, Any]:
    memory = _memory_dir(root)
    index = _load_json(memory / "index.json")
    records = _all_records(root, index)
    by_domain: dict[str, set[str]] = {}
    for identifier, record in records.items():
        by_domain.setdefault(str(record.get("domain")), set()).add(identifier)
    with _write_lock(memory):
        state = _load_json(memory / "state.json")
        _atomic_text(memory / "project-summary.md", _project_summary(_validate_project(state.get("project", {}))))
        known_domain_paths = {path.stem: path for path in (memory / "domains").glob("*.json")}
        for domain_id, record_ids in sorted(by_domain.items()):
            path = _domain_path(memory, domain_id)
            domain = _load_json(path) if path.is_file() else {
                "schema_version": 1, "id": domain_id, "summary": "", "record_ids": [],
            }
            domain["record_ids"] = sorted(record_ids)
            _atomic_json(path, domain)
        for domain_id, path in known_domain_paths.items():
            if domain_id not in by_domain:
                domain = _load_json(path)
                domain["record_ids"] = []
                _atomic_json(path, domain)
        rebuilt = _rebuild_index(root)
    return {
        "status": "REBUILT",
        "records": len(records),
        "domains": len(rebuilt.get("domains", [])),
        "fingerprint": rebuilt.get("fingerprint"),
    }


def benchmark_context(root: Path, package: dict[str, Any], baseline_paths: list[str]) -> dict[str, Any]:
    if not isinstance(package, dict) or package.get("schema_version") != 1:
        raise ProjectMemoryError("context package schema_version must be 1")
    if not isinstance(baseline_paths, list) or not baseline_paths:
        raise ProjectMemoryError("benchmark requires at least one baseline path")
    baseline_bytes = 0
    measured_paths: list[str] = []
    for index, value in enumerate(baseline_paths):
        relative, path = _safe_relative(root, value, f"baseline_paths[{index}]")
        if not path.is_file():
            raise ProjectMemoryError(f"benchmark baseline path is not a file: {relative}")
        baseline_bytes += path.stat().st_size
        measured_paths.append(relative)
    package_bytes = len(_canonical_json(package).encode("utf-8"))
    reduction = 0.0 if baseline_bytes == 0 else max(0.0, (baseline_bytes - package_bytes) * 100.0 / baseline_bytes)
    return {
        "measurement": "UTF-8 bytes",
        "baseline_paths": measured_paths,
        "baseline_bytes": baseline_bytes,
        "context_package_bytes": package_bytes,
        "repeated_context_reduction_percent": round(reduction, 2),
        "limitations": "Byte counts measure repeated material avoided; runtime token usage and elapsed time require runtime instrumentation.",
    }


def validate_memory(root: Path) -> dict[str, Any]:
    project = root.expanduser().resolve()
    memory = _memory_dir(root)
    index = _load_json(memory / "index.json")
    state = _load_json(memory / "state.json")
    if index.get("schema_version") != 1 or state.get("schema_version") != 1:
        raise ProjectMemoryError("project memory schema_version must be 1")
    _validate_project(state.get("project", {}))
    errors: list[str] = []
    records = _all_records(root, index)
    for item in index.get("records", []):
        path = project / str(item.get("path"))
        if not path.is_file() or _file_hash(path) != item.get("sha256"):
            errors.append(f"record index hash mismatch: {item.get('id')}")
    for identifier, record in records.items():
        try:
            _validate_record(root, record)
        except ProjectMemoryError as exc:
            errors.append(str(exc))
            continue
        if record.get("confidence") == "CONFLICTING" and len(record.get("variants", [])) < 2:
            errors.append(f"conflicting record has fewer than two variants: {identifier}")
        for reference in record.get("canonical_refs", []):
            _, path = _safe_relative(root, reference.get("path"), f"record {identifier} canonical reference")
            if not path.exists():
                errors.append(f"record {identifier} canonical reference does not exist: {reference.get('path')}")
        for evidence in record.get("evidence", []):
            _, path = _safe_relative(root, evidence.get("path"), f"record {identifier} evidence")
            if not path.exists():
                errors.append(f"record {identifier} evidence does not exist: {evidence.get('path')}")
            elif evidence.get("sha256") and record.get("status") == "CURRENT" and _file_hash(path) != evidence["sha256"]:
                errors.append(f"record {identifier} current evidence hash is stale: {evidence.get('path')}")
        for relationship in record.get("relationships", []):
            target = str(relationship.get("target"))
            if not relationship.get("external") and target not in records:
                errors.append(f"record {identifier} has dangling relationship target: {target}")
    for item in index.get("domains", []):
        path = project / str(item.get("path"))
        if not path.is_file() or _file_hash(path) != item.get("sha256"):
            errors.append(f"domain index hash mismatch: {item.get('id')}")
            continue
        domain = _load_json(path)
        for identifier in domain.get("record_ids", []):
            if identifier not in records:
                errors.append(f"domain {item.get('id')} has missing record: {identifier}")
    if errors:
        raise ProjectMemoryError("; ".join(errors))
    return {
        "status": "PASS", "domains": len(index.get("domains", [])), "records": len(records),
        "checkpoints": len(index.get("checkpoints", [])), "fingerprint": index.get("fingerprint"),
    }


def _read_object(path: Path, context: str) -> dict[str, Any]:
    value = _load_json(path)
    if not isinstance(value, dict):
        raise ProjectMemoryError(f"{context} must contain an object")
    return value


def _emit(value: dict[str, Any], output: Path | None = None) -> None:
    if output:
        _atomic_json(output, value)
    else:
        print(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create", aliases=["init"], help="create L0 and the hierarchical memory index")
    create.add_argument("--root", required=True, type=Path)
    create.add_argument("--project-file", required=True, type=Path)

    read = subparsers.add_parser("read", aliases=["context"], help="build a bounded task-specific context package")
    read.add_argument("--root", required=True, type=Path)
    read.add_argument("--request-file", required=True, type=Path)
    read.add_argument("--output", type=Path)

    update = subparsers.add_parser("update", aliases=["merge"], help="validate and merge one worker proposal")
    update.add_argument("--root", required=True, type=Path)
    update.add_argument("--proposal-file", required=True, type=Path)

    invalidate = subparsers.add_parser("invalidate", help="selectively invalidate memory from a current source inventory")
    invalidate.add_argument("--root", required=True, type=Path)
    invalidate.add_argument("--inventory", required=True, type=Path)

    for name, help_text in (
        ("compact", "deduplicate indexes and regenerate HOT memory without deleting evidence"),
        ("rebuild", "rebuild summaries and indexes from canonical structured memory records"),
        ("validate", "validate paths, hashes, IDs, relationships, confidence, and conflicts"),
    ):
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument("--root", required=True, type=Path)

    benchmark = subparsers.add_parser("benchmark", help="compare a bounded package with measured baseline files")
    benchmark.add_argument("--root", required=True, type=Path)
    benchmark.add_argument("--package-file", required=True, type=Path)
    benchmark.add_argument("--baseline", action="append", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command in {"create", "init"}:
            result = initialize_memory(args.root, _read_object(args.project_file, "project file"))
        elif args.command in {"read", "context"}:
            result = build_context_package(args.root, _read_object(args.request_file, "context request"))
            _emit(result, args.output)
            return 0
        elif args.command in {"update", "merge"}:
            result = merge_proposal(args.root, _read_object(args.proposal_file, "memory proposal"))
        elif args.command == "invalidate":
            result = invalidate_memory(args.root, _read_object(args.inventory, "source inventory"))
        elif args.command == "compact":
            result = compact_memory(args.root)
        elif args.command == "rebuild":
            result = rebuild_memory(args.root)
        elif args.command == "validate":
            result = validate_memory(args.root)
        else:
            result = benchmark_context(
                args.root, _read_object(args.package_file, "context package"), list(args.baseline),
            )
        _emit(result)
        return 0
    except ProjectMemoryError as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
