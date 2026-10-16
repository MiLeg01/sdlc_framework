#!/usr/bin/env python3
"""Shared loading and validation helpers for Agent Commons evaluations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "evals" / "contracts"
WORKFLOWS = ROOT / "evals" / "workflows" / "contracts.json"
THRESHOLDS = CONTRACTS / "thresholds.json"
CAPABILITY_CONTRACTS = CONTRACTS / "capabilities.json"
AGENT_CONTRACTS = CONTRACTS / "agents.json"
HARD_FAIL_CASES = ROOT / "evals" / "mutations" / "hard-fail-cases.json"
METHODOLOGY_MUTATIONS = ROOT / "evals" / "mutations" / "methodology-cases.json"
PROJECT_FIXTURES = ROOT / "evals" / "fixtures" / "projects" / "index.json"


class EvalConfigError(ValueError):
    """Raised when canonical evaluation configuration is invalid."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvalConfigError(f"cannot load {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise EvalConfigError(f"expected object: {path.relative_to(ROOT)}")
    return value


def load_catalog() -> dict[str, Any]:
    return load_json(ROOT / "catalog" / "capabilities.yaml")


def load_capability_contracts() -> dict[str, Any]:
    capability_data = load_json(CAPABILITY_CONTRACTS)
    agent_data = load_json(AGENT_CONTRACTS)
    combined = dict(capability_data.get("capabilities", {}))
    combined.update(agent_data.get("capabilities", {}))
    return {"schema_version": capability_data.get("schema_version"), "capabilities": combined}


def load_workflows() -> dict[str, Any]:
    return load_json(WORKFLOWS)


def load_thresholds() -> dict[str, Any]:
    return load_json(THRESHOLDS)


def load_hard_fail_assertions() -> set[str]:
    data = load_json(HARD_FAIL_CASES)
    return {
        str(case["assertion"])
        for case in data.get("cases", [])
        if isinstance(case, dict) and case.get("expected_status") == "HARD_FAIL"
    }


def resolve_reference(reference: str, label: str) -> dict[str, Any]:
    path_text, separator, key = reference.partition("#")
    path = (ROOT / path_text).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise EvalConfigError(f"{label} path escapes repository: {reference}") from exc
    data = load_json(path)
    if not separator:
        return data
    value = data.get(key)
    if not isinstance(value, dict):
        raise EvalConfigError(f"missing {label} key {key}: {path_text}")
    return value


def validate_golden_expectation(value: dict[str, Any], label: str) -> list[str]:
    errors: list[str] = []
    identifiers: list[str] = []
    for index, fact in enumerate(value.get("expected_facts", [])):
        if isinstance(fact, str):
            identifiers.append(fact)
            continue
        if not isinstance(fact, dict):
            errors.append(f"{label} expected fact {index} must be a string or object")
            continue
        identifier = fact.get("id")
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"{label} expected fact {index} lacks id")
        else:
            identifiers.append(identifier)
        if fact.get("severity") not in {"CRITICAL", "MAJOR", "MINOR"}:
            errors.append(f"{label} expected fact {index} has invalid severity")
        if not isinstance(fact.get("text"), str) or not fact["text"].strip():
            errors.append(f"{label} expected fact {index} lacks text")
    if len(identifiers) != len(set(identifiers)):
        errors.append(f"{label} has duplicate expected fact IDs")
    return errors


def validate_json_schema(value: Any, schema: dict[str, Any], location: str = "$") -> list[str]:
    """Validate the JSON Schema subset used by the canonical eval protocols."""

    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type is not None:
        type_names = expected_type if isinstance(expected_type, list) else [expected_type]

        def matches(name: str) -> bool:
            return {
                "object": isinstance(value, dict),
                "array": isinstance(value, list),
                "string": isinstance(value, str),
                "integer": isinstance(value, int) and not isinstance(value, bool),
                "number": isinstance(value, (int, float)) and not isinstance(value, bool),
                "boolean": isinstance(value, bool),
                "null": value is None,
            }.get(name, True)

        if not any(matches(name) for name in type_names):
            return [f"{location} must have type {expected_type}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{location} must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{location} must be one of {schema['enum']!r}")
    if isinstance(value, str) and len(value) < schema.get("minLength", 0):
        errors.append(f"{location} is shorter than minLength")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{location} is below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{location} is above maximum")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{location} has too few items")
        if schema.get("uniqueItems"):
            serialized = [json.dumps(item, sort_keys=True) for item in value]
            if len(serialized) != len(set(serialized)):
                errors.append(f"{location} has duplicate items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(validate_json_schema(item, item_schema, f"{location}[{index}]"))
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for required in schema.get("required", []):
            if required not in value:
                errors.append(f"{location} lacks required property {required}")
        for key, item in value.items():
            if key in properties:
                errors.extend(validate_json_schema(item, properties[key], f"{location}.{key}"))
            else:
                additional = schema.get("additionalProperties", True)
                if additional is False:
                    errors.append(f"{location} has unexpected property {key}")
                elif isinstance(additional, dict):
                    errors.extend(validate_json_schema(item, additional, f"{location}.{key}"))
    return errors


def validate_against_schema(value: Any, schema_relative_path: str) -> list[str]:
    return validate_json_schema(value, load_json(ROOT / schema_relative_path))


def catalog_entries(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for kind in catalog.get("capability_kinds", []):
        for identifier, metadata in catalog.get(kind, {}).items():
            entry = dict(metadata)
            entry["kind"] = kind[:-1]
            entries[identifier] = entry
    return entries


def normalize_repo_path(value: str) -> str:
    path = Path(value)
    candidate = path.resolve() if path.is_absolute() else (ROOT / path).resolve()
    try:
        normalized = candidate.relative_to(ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise EvalConfigError(f"changed path escapes repository: {value}") from exc
    if not normalized or normalized == ".":
        raise EvalConfigError(f"invalid changed path: {value}")
    return normalized


def capability_for_path(path: str, entries: dict[str, dict[str, Any]]) -> list[str]:
    matches: list[tuple[int, str]] = []
    for identifier, entry in entries.items():
        configured = str(entry.get("path", "")).rstrip("/")
        if path == configured or path.startswith(configured + "/"):
            matches.append((len(configured), identifier))
    if not matches:
        return []
    longest = max(length for length, _ in matches)
    return sorted(identifier for length, identifier in matches if length == longest)


def impact_graph(catalog: dict[str, Any]) -> dict[str, set[str]]:
    """Return the current catalog's undirected impact graph.

    The canonical catalog exposes ``related`` relationships rather than directional
    dependency edges. Evaluation impact therefore treats a relationship as relevant
    in either change direction and reports this interpretation explicitly.
    """

    entries = catalog_entries(catalog)
    graph = {identifier: set() for identifier in entries}
    for identifier, entry in entries.items():
        for related in entry.get("related", []):
            if related in graph:
                graph[identifier].add(related)
                graph[related].add(identifier)
    return graph


def scenario_ids(identifier: str, contract: dict[str, Any]) -> list[str]:
    return [f"{identifier}:{scenario['id']}" for scenario in contract.get("scenarios", [])]


def validate_configuration() -> list[str]:
    errors: list[str] = []
    catalog = load_catalog()
    entries = catalog_entries(catalog)
    contracts = load_capability_contracts().get("capabilities", {})
    workflows = load_workflows().get("workflows", {})
    thresholds = load_thresholds()
    composition = load_json(ROOT / "archetypes" / "composition.yaml")
    mutation_data = load_json(HARD_FAIL_CASES)
    methodology_mutations = load_json(METHODOLOGY_MUTATIONS)

    for path in (CAPABILITY_CONTRACTS, AGENT_CONTRACTS):
        errors.extend(
            f"{path.relative_to(ROOT)}: {error}"
            for error in validate_against_schema(load_json(path), "evals/schemas/eval-contract.schema.json")
        )
    errors.extend(
        f"{WORKFLOWS.relative_to(ROOT)}: {error}"
        for error in validate_against_schema(load_json(WORKFLOWS), "evals/schemas/workflow-contract.schema.json")
    )
    mutation_cases = mutation_data.get("cases", [])
    mutation_ids = [case.get("id") for case in mutation_cases if isinstance(case, dict)]
    if not mutation_cases:
        errors.append("hard-fail mutation registry has no cases")
    if len(mutation_ids) != len(set(mutation_ids)):
        errors.append("hard-fail mutation registry has duplicate IDs")
    for case in mutation_cases:
        if not isinstance(case, dict) or not case.get("assertion"):
            errors.append("hard-fail mutation case lacks assertion")
        elif case.get("expected_status") != "HARD_FAIL":
            errors.append(f"mutation {case.get('id')} must expect HARD_FAIL")
    for case in methodology_mutations.get("cases", []):
        if not isinstance(case, dict) or not all(
            isinstance(case.get(field), str) and case[field]
            for field in ("id", "target", "search", "replacement", "expected_failure")
        ):
            errors.append("methodology mutation case is incomplete")
            continue
        if not isinstance(case.get("detector"), list) or not case["detector"] or any(
            not isinstance(value, str) or not value for value in case["detector"]
        ):
            errors.append(f"methodology mutation detector is invalid: {case['id']}")
        target = ROOT / case["target"]
        if not target.is_file():
            errors.append(f"methodology mutation target is missing: {case['target']}")
        elif target.read_text(encoding="utf-8").count(case["search"]) != 1:
            errors.append(f"methodology mutation search must match once: {case['id']}")

    project_index = load_json(PROJECT_FIXTURES)
    for project_id, project in project_index.get("projects", {}).items():
        fixture_ref = str(project.get("fixture", ""))
        golden_ref = str(project.get("golden", ""))
        if "/input/" not in fixture_ref or "/golden/" not in golden_ref:
            errors.append(f"project fixture separation is invalid: {project_id}")
            continue
        try:
            fixture = resolve_reference(fixture_ref, "fixture")
            golden = resolve_reference(golden_ref, "golden")
        except EvalConfigError as exc:
            errors.append(str(exc))
            continue
        if any("/golden/" in str(path) for path in fixture.get("source_artifacts", [])):
            errors.append(f"project fixture exposes Golden material to executor: {project_id}")
        errors.extend(validate_golden_expectation(golden, f"project {project_id}"))

    baseline = load_json(ROOT / "evals" / "baselines" / "v1.0.0.json")
    errors.extend(
        f"evals/baselines/v1.0.0.json: {error}"
        for error in validate_against_schema(baseline, "evals/schemas/last-green-baseline.schema.json")
    )

    required_metrics = {
        "correctness",
        "recall",
        "completeness",
        "evidence_grounding",
        "precision",
        "traceability",
        "scope_discipline",
        "handoff_quality",
        "ownership_discipline",
        "consistency",
        "runtime",
        "token_context_efficiency",
        "visual_quality",
    }
    missing_metrics = required_metrics - set(thresholds.get("metrics", {}))
    if missing_metrics:
        errors.append(f"thresholds missing metrics: {sorted(missing_metrics)}")

    for identifier, contract in contracts.items():
        if identifier not in entries:
            errors.append(f"contract uses unknown capability: {identifier}")
            continue
        if contract.get("path") != entries[identifier].get("path"):
            errors.append(f"contract path mismatch: {identifier}")
        metrics = contract.get("applicable_metrics", [])
        unknown_metrics = sorted(set(metrics) - required_metrics)
        if unknown_metrics:
            errors.append(f"{identifier} uses unknown metrics: {unknown_metrics}")
        scenarios = contract.get("scenarios", [])
        if not scenarios:
            errors.append(f"{identifier} has no scenarios")
        scenario_names = [scenario.get("id") for scenario in scenarios]
        if len(scenario_names) != len(set(scenario_names)):
            errors.append(f"{identifier} has duplicate scenario IDs")
        for scenario in scenarios:
            if scenario.get("level") not in {1, 2, 3, 4}:
                errors.append(f"{identifier}:{scenario.get('id')} has invalid level")
            execution_kind = scenario.get("execution", {}).get("kind")
            if execution_kind not in {
                "source-contract",
                "unittest",
                "command",
                "external",
            }:
                errors.append(f"{identifier}:{scenario.get('id')} has invalid execution kind")
            if execution_kind == "external":
                if scenario.get("deterministic") is not False:
                    errors.append(f"{identifier}:{scenario.get('id')} external scenario must be stochastic")
                if scenario.get("judge") != "independent-semantic":
                    errors.append(f"{identifier}:{scenario.get('id')} lacks independent semantic judge")
                for field in ("fixture", "golden"):
                    reference = scenario.get(field)
                    if not isinstance(reference, str) or not reference:
                        errors.append(f"{identifier}:{scenario.get('id')} lacks {field} reference")
                        continue
                    try:
                        resolved = resolve_reference(reference, field)
                    except EvalConfigError as exc:
                        errors.append(str(exc))
                        continue
                    if field == "fixture" and not isinstance(resolved.get("prompt"), str):
                        errors.append(f"{identifier}:{scenario.get('id')} fixture lacks prompt")
                    if field == "fixture":
                        artifacts = resolved.get("source_artifacts")
                        if not isinstance(artifacts, list) or not artifacts:
                            errors.append(f"{identifier}:{scenario.get('id')} fixture lacks source artifacts")
                        else:
                            for artifact in artifacts:
                                if "/golden/" in str(artifact):
                                    errors.append(f"{identifier}:{scenario.get('id')} exposes Golden artifact: {artifact}")
                                artifact_path = (ROOT / str(artifact)).resolve()
                                try:
                                    artifact_path.relative_to(ROOT.resolve())
                                except ValueError:
                                    errors.append(f"{identifier}:{scenario.get('id')} fixture artifact escapes repository: {artifact}")
                                    continue
                                if not artifact_path.is_file():
                                    errors.append(f"{identifier}:{scenario.get('id')} missing fixture artifact: {artifact}")
                        dependencies = resolved.get("workspace_dependencies", [])
                        if not isinstance(dependencies, list):
                            errors.append(f"{identifier}:{scenario.get('id')} workspace dependencies must be a list")
                        else:
                            for dependency in dependencies:
                                if "/golden/" in str(dependency):
                                    errors.append(f"{identifier}:{scenario.get('id')} exposes Golden dependency: {dependency}")
                                dependency_path = (ROOT / str(dependency)).resolve()
                                try:
                                    dependency_path.relative_to(ROOT.resolve())
                                except ValueError:
                                    errors.append(f"{identifier}:{scenario.get('id')} workspace dependency escapes repository: {dependency}")
                                    continue
                                if not dependency_path.exists():
                                    errors.append(f"{identifier}:{scenario.get('id')} missing workspace dependency: {dependency}")
                    if field == "golden" and not (
                        resolved.get("expected_facts") or resolved.get("required_sequence")
                    ):
                        errors.append(f"{identifier}:{scenario.get('id')} golden lacks expectations")
                    if field == "golden":
                        errors.extend(validate_golden_expectation(
                            resolved, f"{identifier}:{scenario.get('id')}",
                        ))
            elif scenario.get("deterministic") is not True:
                errors.append(f"{identifier}:{scenario.get('id')} deterministic execution is not marked deterministic")
            golden = scenario.get("golden")
            if golden:
                try:
                    resolve_reference(str(golden), "golden")
                except EvalConfigError as exc:
                    errors.append(str(exc))

    for workflow_id, workflow in workflows.items():
        unknown = sorted(set(workflow.get("capabilities", [])) - set(entries))
        if unknown:
            errors.append(f"workflow {workflow_id} uses unknown capabilities: {unknown}")
        unknown_metrics = sorted(set(workflow.get("applicable_metrics", [])) - required_metrics)
        if unknown_metrics:
            errors.append(f"workflow {workflow_id} uses unknown metrics: {unknown_metrics}")
        if workflow.get("level") != 4:
            errors.append(f"workflow {workflow_id} must be level 4")
        if not workflow.get("scenarios"):
            errors.append(f"workflow {workflow_id} has no scenarios")
        unknown_archetypes = sorted(set(workflow.get("archetypes", [])) - set(composition.get("archetypes", {})))
        unknown_overlays = sorted(set(workflow.get("overlays", [])) - set(composition.get("overlays", {})))
        if unknown_archetypes:
            errors.append(f"workflow {workflow_id} uses unknown archetypes: {unknown_archetypes}")
        if unknown_overlays:
            errors.append(f"workflow {workflow_id} uses unknown overlays: {unknown_overlays}")
        for scenario in workflow.get("scenarios", []):
            execution_kind = scenario.get("execution", {}).get("kind")
            if scenario.get("level") not in {3, 4}:
                errors.append(f"workflow {workflow_id}:{scenario.get('id')} must be level 3 or 4")
            if execution_kind == "external":
                if scenario.get("deterministic") is not False:
                    errors.append(f"workflow {workflow_id}:{scenario.get('id')} external scenario must be stochastic")
                if scenario.get("judge") != "independent-semantic":
                    errors.append(f"workflow {workflow_id}:{scenario.get('id')} lacks independent semantic judge")
                for field in ("fixture", "golden"):
                    reference = scenario.get(field)
                    if not isinstance(reference, str) or not reference:
                        errors.append(f"workflow {workflow_id}:{scenario.get('id')} lacks {field} reference")
                        continue
                    try:
                        resolved = resolve_reference(reference, field)
                    except EvalConfigError as exc:
                        errors.append(str(exc))
                        continue
                    if field == "fixture" and not isinstance(resolved.get("prompt"), str):
                        errors.append(f"workflow {workflow_id}:{scenario.get('id')} fixture lacks prompt")
                    if field == "fixture":
                        artifacts = resolved.get("source_artifacts")
                        if not isinstance(artifacts, list) or not artifacts:
                            errors.append(f"workflow {workflow_id}:{scenario.get('id')} fixture lacks source artifacts")
                        else:
                            for artifact in artifacts:
                                if "/golden/" in str(artifact):
                                    errors.append(f"workflow {workflow_id}:{scenario.get('id')} exposes Golden artifact: {artifact}")
                                artifact_path = (ROOT / str(artifact)).resolve()
                                try:
                                    artifact_path.relative_to(ROOT.resolve())
                                except ValueError:
                                    errors.append(f"workflow {workflow_id}:{scenario.get('id')} fixture artifact escapes repository: {artifact}")
                                    continue
                                if not artifact_path.is_file():
                                    errors.append(f"workflow {workflow_id}:{scenario.get('id')} missing fixture artifact: {artifact}")
                        dependencies = resolved.get("workspace_dependencies", [])
                        if not isinstance(dependencies, list):
                            errors.append(f"workflow {workflow_id}:{scenario.get('id')} workspace dependencies must be a list")
                        else:
                            for dependency in dependencies:
                                if "/golden/" in str(dependency):
                                    errors.append(f"workflow {workflow_id}:{scenario.get('id')} exposes Golden dependency: {dependency}")
                                dependency_path = (ROOT / str(dependency)).resolve()
                                try:
                                    dependency_path.relative_to(ROOT.resolve())
                                except ValueError:
                                    errors.append(f"workflow {workflow_id}:{scenario.get('id')} workspace dependency escapes repository: {dependency}")
                                    continue
                                if not dependency_path.exists():
                                    errors.append(f"workflow {workflow_id}:{scenario.get('id')} missing workspace dependency: {dependency}")
                    if field == "golden" and not (
                        resolved.get("expected_facts") or resolved.get("required_sequence")
                    ):
                        errors.append(f"workflow {workflow_id}:{scenario.get('id')} golden lacks expectations")
                    if field == "golden":
                        errors.extend(validate_golden_expectation(
                            resolved, f"workflow {workflow_id}:{scenario.get('id')}",
                        ))
            elif scenario.get("deterministic") is not True:
                errors.append(f"workflow {workflow_id}:{scenario.get('id')} deterministic execution is not marked deterministic")
    return errors


def stable_unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))
