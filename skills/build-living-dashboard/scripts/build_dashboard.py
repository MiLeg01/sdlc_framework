#!/usr/bin/env python3
"""Validate structured lifecycle state and generate a single-file dashboard."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "continue-project" / "scripts"))
from brand_profile import (
    accenture_fallback_attributes,
    accenture_fallback_css,
    accenture_fallback_favicon,
    accenture_fallback_logo,
    brand_attributes,
    favicon_markup,
    logo_markup,
    render_brand_css,
    validate_brand_profile,
)
from resolve_project_continuation import apply_action_projection
from validate_dashboard_visual import contract_fingerprint, load_contract as load_visual_contract, resolved_design_fingerprint

COLLECTIONS = {
    "requirement": "requirements", "specification": "specifications",
    "acceptance_criterion": "acceptance_criteria", "implementation_item": "implementation_items",
    "test": "tests", "evidence": "evidence",
}
RELATIONS = {
    "specified-by": ("requirement", "specification"),
    "defines": ("specification", "acceptance_criterion"),
    "implemented-by": (("specification", "acceptance_criterion"), "implementation_item"),
    "validated-by": (("specification", "acceptance_criterion", "implementation_item"), "test"),
    "supported-by": (("requirement", "specification", "test"), "evidence"),
    "depends-on": ("specification", "specification"),
}
REQUIRED_V2 = {"title", "requirements", "specifications", "acceptance_criteria", "relationships"}
SUPPORTED_DASHBOARD_LOCALES = {"en", "de-AT", "de-DE", "de-CH"}
STRUCTURE_PATH = Path(__file__).resolve().parent.parent / "assets" / "dashboard-structure.json"
DOMAIN_BASES = {"MEASURED", "ASSESSED", "MIXED", "UNKNOWN", "NOT_APPLICABLE"}
LOCALIZATION_HASH_PREFIX = "sha256:"
PLACEHOLDER_TRANSLATION_PREFIXES = {
    "translation", "translated", "german", "deutsch", "uebersetzung", "übersetzung",
}
TECHNICAL_FIELD_NAMES = {
    "id", "ids", "source", "source_ref", "source_url", "source_path", "path", "location", "command",
    "url", "uri", "fingerprint", "sha256", "hash", "revision", "requirement_revisions", "updated_at",
    "created_at", "captured_at", "status", "readiness", "implementation_status", "validation_status",
    "confidence", "priority", "category", "kind", "type", "direction", "result", "mode", "schema_version",
    "capability", "subject",
}
TECHNICAL_VALUE = re.compile(
    r"^(?:https?://|file:|[A-Za-z]:[\\/]|(?:\.?\.?/)?(?:[\w.-]+/)+[\w.-]+(?::\d+)?$|"
    r"(?:REQ|SPEC|AC|TEST|EVID|SLICE|ART|CAP)-[A-Za-z0-9._-]+$|(?:pytest|python\d*|node|npm|npx|mvn|gradle)\s)",
    re.IGNORECASE,
)


def _array(data: dict, name: str) -> list[dict]:
    value = data.setdefault(name, [])
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise ValueError(f"{name} must be an array of objects")
    return value


def _legacy(data: dict) -> dict:
    if not {"title", "metrics", "items"} <= data.keys():
        raise ValueError("legacy dashboard data requires title, metrics, and items")
    _array(data, "metrics")
    items = _array(data, "items")
    ids = [str(item.get("id", "")) for item in items]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise ValueError("item IDs must be non-empty and unique")
    data["schema_version"] = 1
    data.setdefault("requirements", [])
    data.setdefault("specifications", [])
    data.setdefault("acceptance_criteria", [])
    data.setdefault("implementation_items", [])
    data.setdefault("tests", [])
    data.setdefault("evidence", [])
    data.setdefault("relationships", [])
    data.setdefault("warnings", [])
    data.setdefault("traceability", [])
    return data


def load_structure() -> dict:
    structure = json.loads(STRUCTURE_PATH.read_text(encoding="utf-8"))
    if structure.get("schema_version") != 2 or not structure.get("sections"):
        raise ValueError("canonical dashboard structure is invalid")
    return structure


def _has_project_records(data: dict, key: str) -> bool:
    value = data.get("project", {}).get(key) if isinstance(data.get("project"), dict) else None
    return bool(value)


def _section_conditions(data: dict) -> dict[str, bool]:
    relationships = data.get("relationships", [])
    return {
        "has_modernization": bool(data.get("implementation_items") or _has_project_records(data, "roadmap")
                                   or _has_project_records(data, "migration") or _has_project_records(data, "modernization")),
        "has_capabilities": _has_project_records(data, "capabilities"),
        "has_requirements": bool(data.get("requirements")),
        "has_specifications": bool(data.get("specifications")),
        "has_flows": _has_project_records(data, "flows"),
        "has_inventory": _has_project_records(data, "inventory"),
        "has_database": bool(_has_project_records(data, "database") or _has_project_records(data, "data_model")),
        "has_interfaces": _has_project_records(data, "interfaces"),
        "has_dependencies": _has_project_records(data, "dependencies"),
        "has_external_estate": bool(_has_project_records(data, "external_estate") or _has_project_records(data, "external_dependencies")),
        "has_application_map": bool(_has_project_records(data, "application_map") or _has_project_records(data, "architecture")),
        "has_traceability": bool(data.get("traceability") or relationships),
        "has_test_quality": bool(data.get("tests") or _has_project_records(data, "test_quality")
                                 or _has_project_records(data, "validation")),
    }


def _project_record(data: dict, key: str) -> object:
    project = data.get("project") if isinstance(data.get("project"), dict) else {}
    return project.get(key)


def _path_value(data: object, path: str) -> object:
    current = data
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def _present(value: object) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


DOMAIN_CONTENT_PATHS = {
    "management-overview": ("project.objective", "project.status", "title"),
    "system-statistics": ("project.composition", "metrics"),
    "complexity": ("project.complexity",),
    "estimation": ("project.modernization.adm_estimate", "project.adm_estimate"),
    "roadmap": ("project.modernization.roadmap", "project.roadmap", "implementation_items"),
    "inventory": ("project.inventory",),
    "system-landscape": ("project.system_landscape", "project.application_map"),
    "component-architecture": ("project.component_architecture", "project.architecture"),
    "service-topology": ("project.topology", "project.service_landscape"),
    "data-persistence": ("project.persistence", "project.database", "project.data_model"),
    "entity-relationship-model": ("project.database", "project.data_model"),
    "integrations": ("project.interfaces",),
    "business-flows-rules": ("project.flows", "project.business_rules"),
    "requirements": ("requirements",),
    "openspec-specifications": ("specifications",),
    "traceability": ("traceability", "relationships"),
    "legacy-test-quality": ("project.test_quality", "project.validation", "tests"),
    "quality-maintainability": ("project.quality", "project.maintainability"),
    "target-architecture": ("project.target_architecture",),
    "risks-decisions": ("project.risks", "project.decisions", "project.open_decisions", "warnings"),
    "open-questions": ("project.stakeholder_questions", "project.questions", "project.technical_questions"),
    "evidence": ("evidence",),
}

COMPLETED_MODERNIZATION_CONTENT = {
    "project.key_findings": "executive findings",
    "project.decision_brief.recommendation": "decision recommendation",
    "project.decision_brief.readiness": "readiness assessment",
    "project.decision_brief.options": "option comparison",
    "project.decision_brief.controls": "decision controls",
    "project.stakeholder_questions.executive": "executive questions",
    "project.stakeholder_questions.questions": "stakeholder question register",
    "project.stakeholder_questions.known_unknowns": "known unknowns",
    "project.stakeholder_questions.open_decisions": "open decisions",
    "project.stakeholder_questions.assumptions": "assumptions",
    "project.modernization.adm_estimate": "modernization estimate",
    "project.modernization.scenarios": "modernization scenarios",
    "project.modernization.roadmap": "modernization roadmap",
    "project.modernization.transition": "transition and coexistence posture",
    "project.modernization.data_interfaces": "data and interface implications",
    "project.modernization.risks_gates": "modernization risks and gates",
}


def semantic_content_failures(data: dict) -> list[str]:
    """Return failures where resolved semantic claims are not backed by meaningful content."""
    failures: list[str] = []
    structure = data.get("dashboard_structure") if isinstance(data.get("dashboard_structure"), dict) else {}
    for domain in structure.get("information_domains", []):
        if not isinstance(domain, dict) or domain.get("status") != "AVAILABLE":
            continue
        identifier = str(domain.get("id", ""))
        candidates = DOMAIN_CONTENT_PATHS.get(identifier, ())
        if candidates and not any(_present(_path_value(data, path)) for path in candidates):
            failures.append(
                f"{identifier}: AVAILABLE has no supporting canonical content "
                f"({', '.join(candidates)})"
            )
    dashboard = data.get("dashboard") if isinstance(data.get("dashboard"), dict) else {}
    analysis = data.get("analysis") if isinstance(data.get("analysis"), dict) else {}
    if dashboard.get("mode") == "full-legacy-modernization" and str(analysis.get("status", "")).upper() in {
        "COMPLETE", "COMPLETE-WITH-BLOCKED-ITEMS",
    }:
        for path, label in COMPLETED_MODERNIZATION_CONTENT.items():
            if not _present(_path_value(data, path)):
                failures.append(f"completed modernization dashboard is missing {label}: {path}")
    return failures


def _validate_shared_claims(data: dict) -> None:
    dashboard = data.get("dashboard") if isinstance(data.get("dashboard"), dict) else {}
    claims = dashboard.setdefault("shared_claims", [])
    if not isinstance(claims, list) or any(not isinstance(item, dict) for item in claims):
        raise ValueError("dashboard.shared_claims must be an array of objects")
    seen: set[str] = set()
    for claim in claims:
        identifier = str(claim.get("id", "")).strip()
        if not identifier or identifier in seen:
            raise ValueError(f"dashboard shared-claim ID must be non-empty and unique: {identifier or '<empty>'}")
        seen.add(identifier)
        paths = claim.get("dashboard_paths")
        markers = claim.get("peer_markers")
        if not isinstance(paths, list) or not paths or any(not isinstance(path, str) or not path.strip() for path in paths):
            raise ValueError(f"dashboard shared claim {identifier} requires dashboard_paths")
        if not isinstance(markers, list) or not markers or any(not isinstance(marker, str) or not marker.strip() for marker in markers):
            raise ValueError(f"dashboard shared claim {identifier} requires peer_markers")
        missing = [path for path in paths if not _present(_path_value(data, path))]
        if missing:
            raise ValueError(f"dashboard shared claim {identifier} has empty dashboard paths: {', '.join(missing)}")


def _dashboard_profile(data: dict, dashboard: dict, structure: dict) -> str:
    explicit = str(dashboard.get("profile", "")).strip()
    if explicit:
        if explicit not in structure["profiles"]:
            raise ValueError(f"unsupported dashboard profile: {explicit}")
        return explicit
    workflow = data.get("workflow") if isinstance(data.get("workflow"), dict) else {}
    scopes = {str(value) for value in workflow.get("scopes", [])}
    if any("legacy" in value for value in scopes):
        return "legacy-modernization"
    if "development" in scopes:
        return "development"
    if "research" in scopes:
        return "research"
    return "general"


def _domain_conditions(data: dict) -> dict[str, bool]:
    project = data.get("project") if isinstance(data.get("project"), dict) else {}
    modernization = project.get("modernization") if isinstance(project.get("modernization"), dict) else {}
    persistence = project.get("persistence") if isinstance(project.get("persistence"), dict) else {}
    topology = project.get("topology") if isinstance(project.get("topology"), dict) else {}
    return {
        "always": True,
        "has_composition": bool(project.get("composition")),
        "has_complexity": bool(project.get("complexity")),
        "has_estimation": bool(project.get("adm_estimate") or modernization.get("adm_estimate")),
        "has_roadmap": bool(project.get("roadmap") or modernization.get("roadmap") or data.get("implementation_items")),
        "has_inventory": bool(project.get("inventory")),
        "has_system_landscape": bool(project.get("system_landscape") or project.get("application_map")),
        "has_component_architecture": bool(project.get("component_architecture") or project.get("architecture")),
        "has_service_topology": bool(topology or project.get("service_landscape")),
        "has_persistence": bool(persistence or project.get("database") or project.get("data_model")),
        "has_relational_schema": bool(persistence.get("relational_detected") is True or project.get("database") or project.get("data_model")),
        "has_interfaces": bool(project.get("interfaces")),
        "has_flows": bool(project.get("flows") or project.get("business_rules")),
        "has_requirements": bool(data.get("requirements")),
        "has_specifications": bool(data.get("specifications")),
        "has_traceability": bool(data.get("traceability") or data.get("relationships")),
        "has_test_quality": bool(project.get("test_quality") or project.get("validation") or data.get("tests")),
        "has_quality": bool(project.get("quality") or project.get("maintainability")),
        "has_target_architecture": bool(project.get("target_architecture")),
        "has_risks_decisions": bool(project.get("risks") or project.get("decisions") or project.get("open_decisions") or data.get("warnings")),
        "has_open_questions": bool(project.get("questions") or project.get("technical_questions") or project.get("stakeholder_questions")),
        "has_evidence": bool(data.get("evidence")),
    }


def _test_quality_summary(quality: dict) -> str:
    """Summarize test strength, keeping mutation state visible even when it was never run.

    Coverage is supporting data and is never presented as a substitute for mutation quality. The
    canonical states are defined in ``assets/dashboard-structure.json`` under ``test_quality_model``.
    """
    parts: list[str] = []
    assessment = str(quality.get("assessment", "")).strip()
    if assessment:
        parts.append(assessment.rstrip("."))
    mutation = quality.get("mutation") if isinstance(quality.get("mutation"), dict) else None
    if mutation is None:
        parts.append("Mutation testing: NOT_YET_ANALYZED")
    else:
        state = str(mutation.get("status", "NOT_YET_ANALYZED")).strip() or "NOT_YET_ANALYZED"
        detail = [f"Mutation testing: {state}"]
        score = mutation.get("score")
        if isinstance(score, (int, float)):
            detail.append(f"score {round(float(score) * 100, 1)}%")
        for field, label in (
            ("critical_survivors", "critical survivors"),
            ("surviving_meaningful_mutants", "meaningful survivors"),
        ):
            value = mutation.get(field)
            if isinstance(value, int):
                detail.append(f"{value} {label}")
        trend = str(mutation.get("trend", "")).strip()
        if trend:
            detail.append(f"trend {trend}")
        reason = str(mutation.get("reason", "")).strip()
        if state in {"NOT_SUPPORTED", "BLOCKED_BY_FLAKY_TESTS"} and reason:
            detail.append(reason.rstrip("."))
        parts.append(", ".join(detail))
    return ". ".join(part for part in parts if part) + "." if parts else ""


def _domain_reason(identifier: str, status: str, data: dict, default: str) -> str:
    project = data.get("project") if isinstance(data.get("project"), dict) else {}
    if identifier == "entity-relationship-model" and status == "NOT_APPLICABLE":
        return "No relational schema detected in the analyzed scope."
    if identifier == "service-topology" and status == "AVAILABLE":
        topology = project.get("topology") if isinstance(project.get("topology"), dict) else {}
        current = str(topology.get("current", "")).strip()
        if current:
            return f"Current topology: {current}."
    if identifier == "legacy-test-quality" and status == "AVAILABLE":
        quality = project.get("test_quality")
        if isinstance(quality, dict):
            summary = _test_quality_summary(quality)
            if summary:
                return summary
    if identifier == "openspec-specifications" and status == "NOT_YET_ANALYZED":
        return "OpenSpec specifications are not yet generated for the current lifecycle stage."
    return default


def _resolve_information_domains(data: dict, dashboard: dict, structure: dict) -> list[dict]:
    allowed_states = set(structure["domain_states"])
    profile = _dashboard_profile(data, dashboard, structure)
    conditions = _domain_conditions(data)
    configured = dashboard.setdefault("domain_states", {})
    if not isinstance(configured, dict):
        raise ValueError("dashboard.domain_states must be an object keyed by information-domain ID")
    canonical_ids = {item["id"] for item in structure["information_domains"]}
    unknown = sorted(set(configured) - canonical_ids)
    if unknown:
        raise ValueError(f"unknown dashboard information domains: {unknown}")
    resolved: list[dict] = []
    for domain in structure["information_domains"]:
        identifier = domain["id"]
        raw = configured.get(identifier)
        explicit = {"status": raw} if isinstance(raw, str) else dict(raw or {})
        if profile not in domain["profiles"]:
            status = "NOT_APPLICABLE"
            reason = f"Not applicable to the {profile} dashboard profile."
        elif identifier == "entity-relationship-model" and isinstance(_project_record(data, "persistence"), dict) and _project_record(data, "persistence").get("relational_detected") is False:
            status = "NOT_APPLICABLE"
            reason = "No relational schema detected in the analyzed scope."
        elif identifier == "target-architecture" and bool(_project_record(data, "analysis_only")):
            status = "NOT_APPLICABLE"
            reason = "Target architecture is outside this analysis-only scope."
        else:
            status = str(explicit.get("status") or ("AVAILABLE" if conditions.get(domain["condition"], False) else "NOT_YET_ANALYZED")).upper()
            reason = str(explicit.get("reason") or (
                "Canonical evidence is available for this information domain."
                if status == "AVAILABLE" else "Waiting for the required canonical analysis state."
            ))
        if status not in allowed_states:
            raise ValueError(f"dashboard domain {identifier} has invalid status: {status}")
        reason = _domain_reason(identifier, status, data, reason)
        basis = str(explicit.get("basis") or "").upper()
        if not basis:
            source = _project_record(data, "composition" if identifier == "system-statistics" else "complexity")
            if isinstance(source, dict) and source.get("basis"):
                basis = str(source["basis"]).upper()
            elif status == "NOT_APPLICABLE":
                basis = "NOT_APPLICABLE"
            elif status == "AVAILABLE" and identifier in {"management-overview", "risks-decisions", "open-questions", "evidence", "legacy-test-quality", "service-topology"}:
                basis = "ASSESSED"
            else:
                basis = "UNKNOWN"
        if basis not in DOMAIN_BASES:
            raise ValueError(f"dashboard domain {identifier} has invalid basis: {basis}")
        if identifier == "system-statistics" and status == "AVAILABLE" and basis != "MEASURED":
            raise ValueError("system-statistics must be MEASURED from deterministic inventory data")
        resolved.append({**domain, "status": status, "reason": reason, "basis": basis})
        configured[identifier] = {"status": status, "reason": reason, "basis": basis}
    dashboard["profile"] = profile
    return resolved


def _resolve_dashboard_structure(data: dict) -> None:
    structure = load_structure()
    dashboard = data.setdefault("dashboard", {})
    if not isinstance(dashboard, dict):
        raise ValueError("dashboard must be an object")
    claimed_status = str(dashboard.get("status", "")).upper()
    if claimed_status in {"VALIDATED", "COMPLETE"}:
        raise ValueError("dashboard status is an external lifecycle-QA result and cannot be claimed in source data")
    registers = dashboard.setdefault("registers", {})
    if not isinstance(registers, dict):
        raise ValueError("dashboard.registers must be an object")
    defaults = {
        "requirements": {"initial_limit": 25},
        "evidence": {"initial_limit": 25},
        "test-quality": {"initial_limit": 25},
        "traceability": {"initial_limit": 50, "max_depth": 5},
    }
    for identifier, default in defaults.items():
        configured = registers.setdefault(identifier, {})
        if not isinstance(configured, dict):
            raise ValueError(f"dashboard.registers.{identifier} must be an object")
        configured.setdefault("initial_limit", default["initial_limit"])
        limit = configured["initial_limit"]
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 200:
            raise ValueError(f"dashboard.registers.{identifier}.initial_limit must be between 1 and 200")
        if identifier == "traceability":
            configured.setdefault("max_depth", default["max_depth"])
            depth = configured["max_depth"]
            if not isinstance(depth, int) or isinstance(depth, bool) or not 2 <= depth <= 5:
                raise ValueError("dashboard.registers.traceability.max_depth must be between 2 and 5")
    enabled = dashboard.setdefault("enabled_sections", [])
    if not isinstance(enabled, list) or any(not isinstance(item, str) for item in enabled):
        raise ValueError("dashboard.enabled_sections must be an array of section IDs")
    known_sections = {item["id"] for item in structure["sections"]}
    unknown_enabled = sorted(set(enabled) - known_sections)
    if unknown_enabled:
        raise ValueError(f"unknown dashboard section IDs: {unknown_enabled}")
    conditions = _section_conditions(data)
    requested_mode = dashboard.get("mode", "canonical")
    if requested_mode not in {"canonical", "adaptive", "full-legacy-modernization"}:
        raise ValueError(f"unsupported dashboard mode: {requested_mode}")
    full_legacy = requested_mode == "full-legacy-modernization"
    canonical_mode = requested_mode == "canonical"
    resolved = []
    for section in structure["sections"]:
        condition_met = conditions.get(section.get("condition", ""), False)
        active = full_legacy or canonical_mode or section["classification"] == "core" or section["id"] in enabled
        if section["classification"] == "conditional":
            active = active or condition_met
        if active:
            applicability = "observed" if section["classification"] == "core" or condition_met else "not-observed"
            if section["id"] == "specifications" and not data.get("openspec_required") and not data.get("specifications"):
                applicability = "not-applicable"
            resolved.append({
                **section,
                "source": "full-legacy-standard" if full_legacy else ("core" if section["classification"] == "core" else (
                    "explicit" if section["id"] in enabled else "data-condition")),
                "applicability": applicability,
            })

    extensions = dashboard.setdefault("extensions", [])
    if not isinstance(extensions, list) or any(not isinstance(item, dict) for item in extensions):
        raise ValueError("dashboard.extensions must be an array of objects")
    extension_points = {item["id"]: item for item in structure["extension_points"]}
    used_ids = set(known_sections)
    for extension in extensions:
        identifier = str(extension.get("id", "")).strip()
        point_id = extension.get("extension_point")
        if not identifier or identifier in used_ids:
            raise ValueError(f"dashboard extension ID must be unique: {identifier or '<empty>'}")
        if point_id not in extension_points:
            raise ValueError(f"unsupported dashboard extension point: {point_id}")
        point = extension_points[point_id]
        order = extension.get("order", point["order_min"])
        if not isinstance(order, int) or not point["order_min"] <= order <= point["order_max"]:
            raise ValueError(f"dashboard extension {identifier} is outside extension point {point_id}")
        title = str(extension.get("title", "")).strip()
        if not title:
            raise ValueError(f"dashboard extension {identifier} requires a title")
        resolved.append({
            "id": identifier, "label": title, "description": str(extension.get("description", "")),
            "classification": "project-specific", "group": point["group"], "order": order,
            "extension_point": point_id, "source": "project-extension",
        })
        used_ids.add(identifier)

    resolved.sort(key=lambda item: (item["order"], item["id"]))
    group_order = {item["id"]: item["order"] for item in structure["navigation"]["groups"]}
    navigation = []
    for group in sorted(structure["navigation"]["groups"], key=lambda item: item["order"]):
        section_ids = [item["id"] for item in resolved if item["group"] == group["id"]]
        if section_ids:
            navigation.append({**group, "section_ids": section_ids})
    if any(group_order.get(item["group"], 999) == 999 for item in resolved):
        raise ValueError("resolved dashboard section uses an unknown navigation group")
    canonical = json.dumps(structure, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    data["dashboard_structure"] = {
        "schema_version": structure["schema_version"],
        "id": structure["id"],
        "fingerprint": hashlib.sha256(canonical.encode()).hexdigest(),
        "navigation_model": structure["navigation"]["model"],
        "mobile_navigation_model": structure["navigation"]["mobile_model"],
        "chrome": structure["chrome"],
        "mode": requested_mode,
        "navigation": navigation,
        "sections": resolved,
        "information_domains": _resolve_information_domains(data, dashboard, structure),
        "interaction_contract": structure["interaction_contract"],
    }


def _resolve_visual_contract(data: dict) -> None:
    contract = load_visual_contract()
    data["dashboard_visual_contract"] = {
        "schema_version": contract["schema_version"],
        "id": contract["id"],
        "contract_fingerprint": contract_fingerprint(contract),
        "design_fingerprint": resolved_design_fingerprint(),
        "branding_policy": contract["design_language"]["branding_policy"],
    }


def _fingerprint(data: dict) -> None:
    derived = {"metrics", "warnings", "traceability", "fingerprint"}
    canonical = json.dumps({k: v for k, v in data.items() if k not in derived}, ensure_ascii=False,
                           sort_keys=True, separators=(",", ":"))
    data["fingerprint"] = hashlib.sha256(canonical.encode()).hexdigest()


def _types(expected: object) -> tuple[str, ...]:
    return expected if isinstance(expected, tuple) else (str(expected),)


def _linked(relationships: list[dict], relation_type: str, source: str | None = None,
            target: str | None = None) -> list[dict]:
    return [relation for relation in relationships if relation["type"] == relation_type
            and (source is None or relation["source"] == source)
            and (target is None or relation["target"] == target)]


def _resolve_criterion_ownership(
    data: dict, index: dict[str, tuple[str, dict]], relationships: list[dict]
) -> None:
    for criterion in data["acceptance_criteria"]:
        criterion_id = criterion["id"]
        definitions = _linked(relationships, "defines", target=criterion_id)
        if len(definitions) != 1:
            raise ValueError(
                f"acceptance criterion {criterion_id} must be defined by exactly one specification"
            )
        specification_id = definitions[0]["source"]
        linked_requirements = sorted({
            relation["source"] for relation in _linked(
                relationships, "specified-by", target=specification_id
            )
        })
        if "requirement_ids" in criterion:
            raise ValueError(
                f"acceptance criterion {criterion_id} has ambiguous requirement ownership; use requirement_id"
            )
        owner = criterion.get("requirement_id")
        if owner is None:
            if len(linked_requirements) == 1:
                owner = linked_requirements[0]
            elif not linked_requirements:
                raise ValueError(
                    f"acceptance criterion {criterion_id} has no owning requirement"
                )
            else:
                raise ValueError(
                    f"acceptance criterion {criterion_id} requires explicit requirement_id because "
                    f"specification {specification_id} serves multiple requirements"
                )
        if owner not in index or index[owner][0] != "requirement":
            raise ValueError(f"acceptance criterion {criterion_id} has invalid requirement owner: {owner}")
        if owner not in linked_requirements:
            raise ValueError(
                f"acceptance criterion {criterion_id} owner {owner} is not linked to specification {specification_id}"
            )
        criterion["requirement_id"] = owner
        criterion["specification_id"] = specification_id


def _is_human_field(field: str, value: str) -> bool:
    normalized = field.casefold()
    if normalized in TECHNICAL_FIELD_NAMES or normalized.endswith(("_id", "_ids", "_path", "_url", "_hash", "_fingerprint")):
        return False
    stripped = value.strip()
    return bool(stripped) and not TECHNICAL_VALUE.search(stripped)


def _collect_human_strings(value: object, path: str, output: dict[str, str], field: str = "") -> None:
    if isinstance(value, str):
        if _is_human_field(field or path.rsplit(".", 1)[-1], value):
            output[path] = value
        return
    if isinstance(value, list):
        if value and all(isinstance(item, str) for item in value):
            if field == "scope":
                joined = ", ".join(value)
                if _is_human_field(field, joined):
                    output[path] = joined
            else:
                for position, item in enumerate(value):
                    if _is_human_field(field or path.rsplit(".", 1)[-1], item):
                        output[f"{path}.{position}"] = item
            return
        for position, item in enumerate(value):
            identity = item.get("id") if isinstance(item, dict) else None
            _collect_human_strings(item, f"{path}.{identity or position}", output, field)
        return
    if isinstance(value, dict):
        for child_field in sorted(value):
            if child_field in {"localization", "brand_profile", "dashboard_structure", "dashboard_visual_contract"}:
                continue
            _collect_human_strings(value[child_field], f"{path}.{child_field}", output, child_field)


def rendered_localization_sources(data: dict) -> dict[str, str]:
    """Return the deterministic human-readable source strings that the dashboard can render."""
    sources: dict[str, str] = {}
    for field in ("title", "subtitle"):
        value = data.get(field)
        if isinstance(value, str) and value.strip():
            sources[f"data.{field}"] = value
    project = data.get("project")
    if isinstance(project, dict):
        for field in ("status", "context_label"):
            value = project.get(field)
            if isinstance(value, str) and value.strip():
                sources[f"project.{field}"] = value
        _collect_human_strings(project, "project", sources)
    structure = data.get("dashboard_structure")
    if isinstance(structure, dict):
        statuses: set[str] = set()
        for domain in structure.get("information_domains", []):
            if not isinstance(domain, dict) or not domain.get("id"):
                continue
            identifier = str(domain["id"])
            for field in ("label", "reason"):
                value = domain.get(field)
                if isinstance(value, str) and value.strip():
                    sources[f"domain.{identifier}.{field}"] = value
            status = str(domain.get("status", "")).strip()
            if status:
                statuses.add(status)
        for status in sorted(statuses):
            sources[f"domain.status.{status}"] = status
    for item_type, collection in COLLECTIONS.items():
        for item in data.get(collection, []):
            prefix = str(item.get("i18n_key") or f"{item_type}.{item['id']}")
            for field in sorted(item):
                if field in {"id", "i18n_key"}:
                    continue
                _collect_human_strings(item[field], f"{prefix}.{field}", sources, field)
    dashboard = data.get("dashboard")
    if isinstance(dashboard, dict):
        for extension in dashboard.get("extensions", []):
            if isinstance(extension, dict):
                prefix = f"extension.{extension.get('id', 'unknown')}"
                for field in ("title", "description", "summary", "content", "items"):
                    if field in extension:
                        _collect_human_strings(extension[field], f"{prefix}.{field}", sources, field)
    for warning in data.get("warnings", []):
        if isinstance(warning, dict) and isinstance(warning.get("message"), str):
            sources[f"warning.{warning.get('code', 'UNKNOWN')}.detail"] = warning["message"]
    return dict(sorted(sources.items()))


def _validate_localization_coverage(data: dict) -> None:
    delivery = data["delivery"]
    target_locales = [locale for locale in delivery["languages"] if locale != "en"]
    sources = rendered_localization_sources(data)
    data["localization_coverage"] = {
        "source_locale": "en", "required_locales": target_locales,
        "rendered_human_field_count": len(sources),
        "source_fingerprint": hashlib.sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest(),
    }
    if not target_locales:
        return
    localization = data.get("localization")
    messages = localization.get("messages") if isinstance(localization, dict) else None
    if not isinstance(messages, dict):
        raise ValueError("multilingual dashboard requires localization.messages")
    failures: list[str] = []
    for key, source in sources.items():
        record = messages.get(key)
        if not isinstance(record, dict):
            failures.append(f"missing message {key}")
            continue
        if record.get("source") != source:
            failures.append(f"stale source {key}")
        expected_hash = LOCALIZATION_HASH_PREFIX + hashlib.sha256(source.encode()).hexdigest()
        if record.get("source_hash") != expected_hash:
            failures.append(f"stale source hash {key}")
        translations = record.get("translations")
        if not isinstance(translations, dict):
            failures.append(f"missing translations {key}")
            continue
        for locale in target_locales:
            translated = translations.get(locale)
            if not isinstance(translated, str) or not translated.strip():
                failures.append(f"missing translation {key}:{locale}")
            elif translated.strip() == source.strip() and not record.get("allow_identical", False):
                failures.append(f"unintentionally identical translation {key}:{locale}")
            elif _looks_like_placeholder_translation(translated, source, locale):
                failures.append(f"placeholder translation {key}:{locale}")
    if failures:
        raise ValueError("localization coverage failed: " + "; ".join(failures))
    data["localization_coverage"]["status"] = "PASS"


def _looks_like_placeholder_translation(translated: str, source: str, locale: str) -> bool:
    value = translated.strip()
    language = locale.split("-", 1)[0].lower()
    prefixes = PLACEHOLDER_TRANSLATION_PREFIXES | {language, locale.lower()}
    for prefix in prefixes:
        pattern = rf"^(?:\[{re.escape(prefix)}\]|{re.escape(prefix)})(?:\s*[:\-]\s*|\s+)"
        stripped = re.sub(pattern, "", value, count=1, flags=re.IGNORECASE)
        if stripped != value and stripped.strip() == source.strip():
            return True
    return False


def _validate_analysis_projection(data: dict) -> None:
    analysis = data.get("analysis")
    if analysis is None:
        return
    if not isinstance(analysis, dict):
        raise ValueError("analysis must be an object")
    target_mode = str(analysis.get("target_mode") or analysis.get("mode") or "").upper()
    if target_mode not in {"FULL", "BOUNDED"}:
        raise ValueError("analysis.target_mode must be FULL or BOUNDED")
    coverage = analysis.get("coverage")
    if not isinstance(coverage, dict):
        raise ValueError("analysis.coverage must be an object")
    counts: dict[str, int] = {}
    for key in ("relevant", "accounted", "unaccounted", "blocked"):
        value = coverage.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"analysis.coverage.{key} must be a non-negative integer")
        counts[key] = value
    if counts["accounted"] + counts["unaccounted"] != counts["relevant"]:
        raise ValueError("analysis coverage totals do not reconcile")
    status = str(analysis.get("status") or "IN-PROGRESS").upper()
    if status in {"COMPLETE", "COMPLETE-WITH-BLOCKED-ITEMS"} and counts["unaccounted"]:
        raise ValueError("analysis cannot be complete while relevant artifacts are unaccounted")
    project = data.setdefault("project", {})
    if not isinstance(project, dict):
        raise ValueError("project must be an object")
    if counts["unaccounted"] and "complete" in str(project.get("status", "")).casefold():
        raise ValueError("partial analysis dashboard must not claim complete project status")


def _derive(data: dict, index: dict[str, tuple[str, dict]]) -> None:
    requirements, specifications = data["requirements"], data["specifications"]
    relationships, tests = data["relationships"], data["tests"]
    test_by_id = {item["id"]: item for item in tests}
    req_by_id = {item["id"]: item for item in requirements}
    warnings: list[dict] = []

    for requirement in requirements:
        specification_ids = [r["target"] for r in _linked(relationships, "specified-by", source=requirement["id"])]
        requirement["specification_ids"] = specification_ids
        requirement["evidence_ids"] = [r["target"] for r in _linked(
            relationships, "supported-by", source=requirement["id"]
        )]
        if data.get("openspec_required", False) and requirement.get("status") == "approved" and not specification_ids:
            warnings.append({"code": "APPROVED_REQUIREMENT_UNSPECIFIED", "subject": requirement["id"],
                             "message": "Approved requirement has no OpenSpec specification."})
        if (data.get("openspec_required", False) and requirement.get("implementation_status") in
                {"implemented", "validated"} and not specification_ids):
            warnings.append({"code": "IMPLEMENTED_WITHOUT_SPECIFICATION", "subject": requirement["id"],
                             "message": "Requirement is implemented without a required specification."})

    for specification in specifications:
        spec_id = specification["id"]
        requirement_ids = [r["source"] for r in _linked(relationships, "specified-by", target=spec_id)]
        criterion_ids = [r["target"] for r in _linked(relationships, "defines", source=spec_id)]
        specification["requirement_ids"] = requirement_ids
        specification["acceptance_criterion_ids"] = criterion_ids
        specification["dependency_ids"] = [r["target"] for r in _linked(relationships, "depends-on", source=spec_id)]
        specification["implementation_item_ids"] = [r["target"] for r in _linked(
            relationships, "implemented-by", source=spec_id
        )]
        specification["evidence_ids"] = [r["target"] for r in _linked(
            relationships, "supported-by", source=spec_id
        )]
        linked_sources = {spec_id} | set(criterion_ids)
        specification["test_ids"] = sorted({r["target"] for r in relationships
                                             if r["type"] == "validated-by" and r["source"] in linked_sources})
        if not requirement_ids and not specification.get("source_rationale"):
            warnings.append({"code": "SPECIFICATION_WITHOUT_RATIONALE", "subject": spec_id,
                             "message": "Specification has no requirement or source rationale."})
        unresolved = [cid for cid in criterion_ids if index[cid][1].get("status") in {"draft", "pending", "blocked"}]
        if specification.get("readiness") == "ready" and unresolved:
            warnings.append({"code": "READY_WITH_UNRESOLVED_CRITERIA", "subject": spec_id,
                             "message": f"Ready specification has unresolved criteria: {', '.join(unresolved)}."})
        if specification.get("implementation_status") in {"implemented", "validated"} and not specification["test_ids"]:
            warnings.append({"code": "IMPLEMENTED_WITHOUT_TESTS", "subject": spec_id,
                             "message": "Implemented specification has no linked tests."})

        snapshots = specification.get("requirement_revisions", {})
        stale = [req_id for req_id in requirement_ids
                 if str(snapshots.get(req_id, "")) != str(req_by_id[req_id].get("revision", ""))]
        specification["stale_requirement_ids"], specification["stale"] = stale, bool(stale)
        if stale:
            warnings.append({"code": "STALE_SPECIFICATION", "subject": spec_id,
                             "message": f"Requirement revision changed: {', '.join(stale)}."})

        uncovered: list[str] = []
        failing = False
        blocked = specification.get("status") == "blocked" or specification.get("readiness") == "blocked"
        for criterion_id in criterion_ids:
            linked_test_ids = {r["target"] for r in _linked(relationships, "validated-by", source=criterion_id)}
            criterion = index[criterion_id][1]
            criterion["implementation_item_ids"] = [r["target"] for r in _linked(
                relationships, "implemented-by", source=criterion_id
            )]
            criterion["test_ids"] = sorted(linked_test_ids)
            passing = any(test_by_id[test_id].get("status") == "passing" for test_id in linked_test_ids)
            failing = failing or any(test_by_id[test_id].get("status") == "failing" for test_id in linked_test_ids)
            blocked = blocked or index[criterion_id][1].get("status") == "blocked"
            if not passing:
                uncovered.append(criterion_id)
        specification["uncovered_acceptance_criterion_ids"] = uncovered
        if uncovered:
            warnings.append({"code": "UNCOVERED_ACCEPTANCE_CRITERIA", "subject": spec_id,
                             "message": f"No passing test proves: {', '.join(uncovered)}."})
        if blocked:
            validation = "BLOCKED"
        elif failing:
            validation = "FAIL"
        elif criterion_ids and not uncovered and specification.get("implementation_status") in {"implemented", "validated"}:
            validation = "PASS"
        else:
            validation = "PARTIAL"
        specification["validation_status"] = validation

    for test in tests:
        test["evidence_ids"] = [r["target"] for r in _linked(
            relationships, "supported-by", source=test["id"]
        )]

    approved = [item for item in requirements if item.get("status") == "approved"]
    specified = [item for item in approved if item["specification_ids"]]
    analysis_metrics: list[dict] = []
    if isinstance(data.get("analysis"), dict):
        analysis = data["analysis"]
        coverage = analysis["coverage"]
        slices = analysis.get("slices", {}) if isinstance(analysis.get("slices"), dict) else {}
        analysis_metrics = [
            {"i18n_key": "metric.source_accounted", "label": "Source accounted", "value": f"{coverage['accounted']} / {coverage['relevant']}",
             "status": "good" if coverage["unaccounted"] == 0 else "risk"},
            {"i18n_key": "metric.unaccounted_source", "label": "Unaccounted source", "value": coverage["unaccounted"],
             "status": "good" if coverage["unaccounted"] == 0 else "risk"},
            {"i18n_key": "metric.analysis_slices", "label": "Analysis slices", "value": f"{slices.get('validated', 0)} / {slices.get('total', 0)}",
             "status": "good" if slices.get("total", 0) and slices.get("validated") == slices.get("total") else "neutral"},
            {"i18n_key": "metric.blocked_source", "label": "Blocked source", "value": coverage["blocked"],
             "status": "risk" if coverage["blocked"] else "good"},
        ]
    data["metrics"] = analysis_metrics + [
        {"i18n_key": "metric.requirements", "label": "Requirements", "value": len(requirements), "status": "neutral"},
        {"i18n_key": "metric.specifications", "label": "Specifications", "value": len(specifications), "status": "neutral"},
        {"i18n_key": "metric.approved_specified", "label": "Approved specified", "value": f"{len(specified)} / {len(approved)}", "status": "good" if len(specified) == len(approved) else "risk"},
        {"i18n_key": "metric.unspecified_approved", "label": "Unspecified approved", "value": len(approved) - len(specified), "status": "risk" if len(approved) != len(specified) else "good"},
        {"i18n_key": "metric.ready_specs", "label": "Ready specs", "value": sum(item.get("readiness") == "ready" and not item["stale"] for item in specifications), "status": "neutral"},
        {"i18n_key": "metric.in_implementation", "label": "In implementation", "value": sum(item.get("implementation_status") == "in-progress" for item in specifications), "status": "neutral"},
        {"i18n_key": "metric.implemented", "label": "Implemented", "value": sum(item.get("implementation_status") in {"implemented", "validated"} for item in specifications), "status": "neutral"},
        {"i18n_key": "metric.validated", "label": "Validated", "value": sum(item["validation_status"] == "PASS" for item in specifications), "status": "good"},
    ]
    data["warnings"] = warnings
    data["traceability"] = []
    for requirement in requirements:
        for spec_id in requirement["specification_ids"]:
            criterion_ids = [criterion_id for criterion_id in index[spec_id][1]["acceptance_criterion_ids"]
                             if index[criterion_id][1]["requirement_id"] == requirement["id"]] or [None]
            for criterion_id in criterion_ids:
                implementation_ids = ([r["target"] for r in _linked(
                    relationships, "implemented-by", source=criterion_id
                )] if criterion_id else []) or [None]
                criterion_test_ids = ([r["target"] for r in _linked(
                    relationships, "validated-by", source=criterion_id
                )] if criterion_id else [])
                for implementation_id in implementation_ids:
                    implementation_test_ids = ([r["target"] for r in _linked(
                        relationships, "validated-by", source=implementation_id
                    )] if implementation_id else [])
                    test_ids = implementation_test_ids or criterion_test_ids or [None]
                    for test_id in test_ids:
                        data["traceability"].append({
                            "requirement": requirement["id"], "specification": spec_id,
                            "acceptance_criterion": criterion_id,
                            "implementation_item": implementation_id, "test": test_id,
                        })
def validate(data: object) -> dict:
    if not isinstance(data, dict):
        raise ValueError("dashboard data must be an object")
    if data.get("schema_version", 1) == 1:
        data = _legacy(data)
        _resolve_dashboard_structure(data)
        _resolve_visual_contract(data)
        _fingerprint(data)
        return data
    missing = REQUIRED_V2 - data.keys()
    if missing:
        raise ValueError(f"missing keys: {sorted(missing)}")
    for name in COLLECTIONS.values():
        _array(data, name)
    relationships = _array(data, "relationships")
    index: dict[str, tuple[str, dict]] = {}
    for item_type, collection in COLLECTIONS.items():
        for item in data[collection]:
            identifier = str(item.get("id", "")).strip()
            if not identifier:
                raise ValueError(f"{collection} IDs must be non-empty")
            if identifier in index:
                raise ValueError(f"duplicate lifecycle ID: {identifier}")
            item["id"] = identifier
            index[identifier] = (item_type, item)
    for relation in relationships:
        relation_type = relation.get("type")
        if relation_type not in RELATIONS:
            raise ValueError(f"unsupported relationship type: {relation_type}")
        source, target = relation.get("source"), relation.get("target")
        if source not in index or target not in index:
            raise ValueError(f"relationship endpoint missing: {source} -> {target}")
        expected_source, expected_target = RELATIONS[relation_type]
        if index[source][0] not in _types(expected_source) or index[target][0] not in _types(expected_target):
            raise ValueError(f"invalid endpoint types for {relation_type}: {source} -> {target}")
    _resolve_criterion_ownership(data, index, relationships)
    brand_required = data.get("brand_required", False)
    if not isinstance(brand_required, bool):
        raise ValueError("brand_required must be boolean")
    if data.get("brand_profile") is not None:
        data["brand_profile"] = validate_brand_profile(data["brand_profile"])
        if brand_required and not data["brand_profile"]["required"]:
            raise ValueError("dashboard requires branding but the supplied profile is optional")
    elif brand_required:
        data["brand_status"] = "fallback"
        data["brand_fallback"] = "accenture"
        data.setdefault("brand_fallback_reason", "required brand profile unavailable")
    delivery = data.setdefault("delivery", {
        "languages": ["en"], "default_language": "en", "language_switch": False,
        "storage_key": "living-dashboard-language",
    })
    if not isinstance(delivery, dict):
        raise ValueError("delivery must be an object")
    languages = delivery.get("languages", ["en"])
    if not isinstance(languages, list) or not languages or any(
        not isinstance(locale, str) or locale not in SUPPORTED_DASHBOARD_LOCALES for locale in languages
    ):
        raise ValueError(f"delivery.languages must use {sorted(SUPPORTED_DASHBOARD_LOCALES)}")
    languages = list(dict.fromkeys(languages))
    default_language = delivery.get("default_language", languages[0])
    if default_language not in languages:
        raise ValueError("delivery.default_language must be included in delivery.languages")
    language_switch = delivery.get("language_switch", len(languages) > 1)
    if not isinstance(language_switch, bool):
        raise ValueError("delivery.language_switch must be boolean")
    if language_switch and len(languages) < 2:
        raise ValueError("delivery.language_switch requires at least two languages")
    storage_key = delivery.get("storage_key", "living-dashboard-language")
    if not isinstance(storage_key, str) or not storage_key.strip():
        raise ValueError("delivery.storage_key must be a non-empty string")
    delivery.update({
        "languages": languages,
        "default_language": default_language,
        "language_switch": language_switch,
        "storage_key": storage_key,
    })
    _validate_analysis_projection(data)
    _derive(data, index)
    workflow = data.setdefault("workflow", {
        "scopes": [],
        "requirements_required": bool(data.get("requirements")),
        "specification_method": "openspec" if data.get("openspec_required") else "none",
        "specifications_required": bool(data.get("openspec_required")),
        "implementation_phase": "active" if data.get("implementation_items") else "none",
        "source_inventory_complete": True,
        "requires_user_choice": False,
        "dashboard_enabled": True,
    })
    if not isinstance(workflow, dict):
        raise ValueError("workflow must be an object")
    apply_action_projection(workflow, data)
    _resolve_dashboard_structure(data)
    _validate_shared_claims(data)
    content_failures = semantic_content_failures(data)
    if content_failures:
        raise ValueError("dashboard semantic content failed: " + "; ".join(content_failures))
    _validate_localization_coverage(data)
    _resolve_visual_contract(data)
    _fingerprint(data)
    return data


def _render_navigation(data: dict) -> str:
    section_by_id = {item["id"]: item for item in data["dashboard_structure"]["sections"]}
    groups = []
    for group in data["dashboard_structure"]["navigation"]:
        links = []
        for section_id in group["section_ids"]:
            section = section_by_id[section_id]
            links.append(
                f'<a href="#{html.escape(section_id)}" data-section-target="{html.escape(section_id)}">'
                f'<strong data-i18n="section.{html.escape(section_id)}.label">{html.escape(section["label"])}</strong>'
                f'<small data-i18n="section.{html.escape(section_id)}.description">{html.escape(section.get("description", ""))}</small>'
                '</a>'
            )
        groups.append(
            f'<details class="nav-group" data-nav-group="{html.escape(group["id"])}">'
            f'<summary><span class="nav-long" data-i18n="group.{html.escape(group["id"])}.label">{html.escape(group["label"])}</span>'
            f'<span class="nav-short">{html.escape(group["short_label"])}</span><span class="nav-chevron" aria-hidden="true"></span></summary>'
            f'<div class="nav-menu" role="group">{"".join(links)}</div></details>'
        )
    return "".join(groups)


def _render_section_contract(section: dict, domains: list[dict]) -> str:
    nodes = []
    domain_node = ""
    if domains:
        cards = "".join(
            f'<article class="generic-item searchable" data-information-domain="{html.escape(domain["id"])}" '
            f'data-domain-status="{html.escape(domain["status"])}" data-domain-basis="{html.escape(domain["basis"])}">'
            f'<strong data-i18n="domain.{html.escape(domain["id"])}.label">{html.escape(domain["label"])}</strong>'
            f'<p><span class="status-chip {html.escape(domain["status"].lower().replace("_", "-"))}" '
            f'data-i18n="domain.status.{html.escape(domain["status"])}">{html.escape(domain["status"])}</span> '
            f'<span data-i18n="domain.{html.escape(domain["id"])}.reason">{html.escape(domain["reason"])}</span></p></article>'
            for domain in domains
        )
        domain_node = f'<div class="generic-grid domain-status-list" data-dashboard-region="information-domains">{cards}</div>'
    for region in section.get("required_regions", []):
        nodes.append(f'<div class="contract-region" data-dashboard-region="{html.escape(region)}"></div>')
    for hook in section.get("required_hooks", []):
        if hook == "filter":
            nodes.append(
                f'<label class="section-filter" data-dashboard-hook="filter"><span data-i18n="ui.filter">Filter</span>'
                f'<input type="search" data-section-filter="{html.escape(section["id"])}" placeholder="Search records" aria-label="Filter {html.escape(section["label"])}" data-i18n-attr="aria-label:ui.search_placeholder,placeholder:ui.search_placeholder"></label>'
            )
        elif hook == "record-list":
            nodes.append('<div class="record-list" data-dashboard-hook="record-list"></div>')
        elif hook == "trace-chain":
            nodes.append('<div class="trace-list" data-dashboard-hook="trace-chain"></div>')
        elif hook == "detail-opener":
            nodes.append('<span class="detail-opener-contract" data-dashboard-hook="detail-opener" aria-hidden="true"></span>')
    if domain_node:
        nodes.append(domain_node)
    if not nodes:
        nodes.append('<div class="section-content" data-section-content></div>')
    return "".join(nodes)


def _render_sections(data: dict) -> str:
    sections = []
    domains_by_section: dict[str, list[dict]] = {}
    for domain in data["dashboard_structure"].get("information_domains", []):
        domains_by_section.setdefault(domain["section_id"], []).append(domain)
    project = data.get("project") if isinstance(data.get("project"), dict) else {}
    watermark = str(project.get("watermark") or str(data.get("title", "Project")).split()[0]).upper()[:18]
    for section in data["dashboard_structure"]["sections"]:
        watermark_attribute = f' data-watermark="{html.escape(watermark)}"' if section["id"] == "overview" else ""
        sections.append(
            f'<section id="{html.escape(section["id"])}" class="view view-{html.escape(section["id"])}" '
            f'data-canonical-section="{html.escape(section["id"])}" data-section-order="{section["order"]}" '
            f'data-section-classification="{html.escape(section["classification"])}" '
            f'data-section-applicability="{html.escape(section.get("applicability", "observed"))}"{watermark_attribute}>'
            f'<header class="section-heading"><div><p class="eyebrow" data-i18n="group.{html.escape(section["group"])}.label">{html.escape(section["group"])}</p>'
            f'<h2 data-i18n="section.{html.escape(section["id"])}.label">{html.escape(section["label"])}</h2>'
            f'<p data-i18n="section.{html.escape(section["id"])}.description">{html.escape(section.get("description", ""))}</p></div>'
            f'<span class="section-class" data-i18n="classification.{html.escape(section["classification"])}">{html.escape(section["classification"])}</span></header>'
            f'<div class="section-body">{_render_section_contract(section, domains_by_section.get(section["id"], []))}</div></section>'
        )
    return "".join(sections)


def render(data: dict, shell: str) -> str:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    runtime_path = Path(__file__).resolve().parents[2] / "localize-client-artifact" / "assets" / "bilingual-runtime.js"
    runtime = runtime_path.read_text(encoding="utf-8")
    profile = data.get("brand_profile")
    brand_id = str(profile["id"] if profile else "accenture-fallback")
    brand_status = str(profile["status"] if profile else "fallback")
    brand_fingerprint = str(profile["profile_fingerprint"] if profile else "")
    brand_css = render_brand_css(profile) if profile else accenture_fallback_css()
    rendered_brand_attributes = brand_attributes(profile) if profile else accenture_fallback_attributes()
    rendered_favicon = favicon_markup(profile) if profile else accenture_fallback_favicon()
    rendered_logo = logo_markup(profile, "brand-logo") if profile else accenture_fallback_logo("brand-logo")
    delivery = data["delivery"]
    flag_by_locale = {"de-AT": "🇦🇹", "de-DE": "🇩🇪", "de-CH": "🇨🇭", "en": "🇬🇧"}
    accessible_name_by_locale = {
        "de-AT": "Deutsch (Österreich)", "de-DE": "Deutsch (Deutschland)",
        "de-CH": "Deutsch (Schweiz)", "en": "English",
    }
    rendered_language_switch_buttons = ""
    if delivery["language_switch"] and len(delivery["languages"]) > 1:
        rendered_language_switch_buttons = "".join(
            f'<button type="button" role="radio" data-localization-locale="{html.escape(locale)}" '
            f'aria-checked="{str(locale == delivery["default_language"]).lower()}" '
            f'tabindex="{0 if locale == delivery["default_language"] else -1}" '
            f'aria-label="{html.escape(accessible_name_by_locale.get(locale, locale))}"><span aria-hidden="true">'
            f'{flag_by_locale.get(locale, "🌐")}</span></button>'
            for locale in delivery["languages"]
        )
    co_brand = data.get("project", {}).get("co_brand")
    rendered_co_brand = (
        f'<span class="co-brand" data-dashboard-hook="co-brand">{html.escape(str(co_brand))}</span>'
        if co_brand else '<span class="co-brand" data-dashboard-hook="co-brand" hidden></span>'
    )
    return (shell.replace("__TITLE__", html.escape(str(data["title"])))
            .replace("__BRAND__", html.escape(str(data.get("brand", "project"))))
            .replace("__BRAND_ID__", html.escape(brand_id))
            .replace("__BRAND_STATUS__", html.escape(brand_status))
            .replace("__BRAND_PROFILE_FINGERPRINT__", html.escape(brand_fingerprint))
            .replace("__BRAND_ATTRIBUTES__", rendered_brand_attributes)
            .replace("__BRAND_FAVICON__", rendered_favicon)
            .replace("__BRAND_LOGO__", rendered_logo)
            .replace("__CO_BRAND__", rendered_co_brand)
            .replace("__LANGUAGE_SWITCH_BUTTONS__", rendered_language_switch_buttons)
            .replace("__DASHBOARD_DESIGN_ID__", html.escape(str(data["dashboard_visual_contract"]["id"])))
            .replace("__DASHBOARD_DESIGN_FINGERPRINT__", html.escape(str(data["dashboard_visual_contract"]["design_fingerprint"])))
            .replace("__BRAND_STYLE__", brand_css)
            .replace("__NAVIGATION__", _render_navigation(data))
            .replace("__SECTIONS__", _render_sections(data))
            .replace("__LOCALIZATION_RUNTIME__", runtime)
            .replace("__DATA__", payload))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--brand-profile", type=Path)
    parser.add_argument("--dashboard-mode", choices=["adaptive", "full-legacy-modernization"])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    source_data = json.loads(args.data.read_text(encoding="utf-8"))
    if args.dashboard_mode:
        source_data.setdefault("dashboard", {})["mode"] = args.dashboard_mode
    if args.brand_profile:
        try:
            supplied_profile = validate_brand_profile(json.loads(args.brand_profile.read_text(encoding="utf-8")))
            embedded_profile = source_data.get("brand_profile")
            if embedded_profile is not None:
                embedded_profile = validate_brand_profile(embedded_profile)
                if embedded_profile["profile_fingerprint"] != supplied_profile["profile_fingerprint"]:
                    raise ValueError("embedded and supplied brand profiles differ")
            source_data["brand_profile"] = supplied_profile
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            source_data.pop("brand_profile", None)
            source_data["brand_required"] = True
            source_data["brand_status"] = "fallback"
            source_data["brand_fallback"] = "accenture"
            source_data["brand_requested_source"] = str(args.brand_profile)
            source_data["brand_fallback_reason"] = str(exc)
            print(f"client branding unavailable; using Accenture fallback: {exc}", file=sys.stderr)
    data = validate(source_data)
    shell = (Path(__file__).resolve().parent.parent / "assets" / "dashboard-shell.html").read_text(encoding="utf-8")
    expected = render(data, shell)
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != expected:
            print(f"dashboard drift: {args.output}")
            return 1
        print(f"dashboard current: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(expected, encoding="utf-8")
    temporary.replace(args.output)
    print(f"generated {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
