#!/usr/bin/env python3
"""Create a minimal, non-overwriting project scaffold from resolved choices."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import sys
import time
from pathlib import Path

from brief_intake import interactive_questions, parse_brief
from client_delivery_policy import (
    CONFIRMED,
    HIGH_CONFIDENCE,
    NOT_PUBLIC_SECTOR,
    detect_client_context,
    normalize_country,
    normalize_locale,
    public_sector_defaults,
)

LIBRARY_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(LIBRARY_ROOT / "tools"))
sys.path.insert(0, str(LIBRARY_ROOT / "skills" / "build-living-dashboard" / "scripts"))
sys.path.insert(0, str(LIBRARY_ROOT / "skills" / "create-branded-html-artifact" / "scripts"))
sys.path.insert(0, str(LIBRARY_ROOT / "skills" / "continue-project" / "scripts"))

from resolve_archetypes import (  # noqa: E402
    CompositionError,
    load_contract,
    registry_aliases,
    resolve_composition,
    split_values,
)
from resolve_capability_gaps import CapabilityGapError, assess as assess_capability_gaps  # noqa: E402
from build_dashboard import render as render_dashboard, validate as validate_dashboard  # noqa: E402
from brand_profile import (  # noqa: E402
    accenture_fallback_attributes,
    accenture_fallback_css,
    accenture_fallback_favicon,
    accenture_fallback_logo,
    validate_brand_profile,
)
from render_branded_html import render as render_branded_presentation  # noqa: E402
from plan_parallel_execution import plan_execution  # noqa: E402
from resolve_project_continuation import initial_next_action  # noqa: E402
import external_capabilities  # noqa: E402

CONTRACT = load_contract()
ARCHETYPE_ALIASES = registry_aliases(CONTRACT)
SCOPES = set(ARCHETYPE_ALIASES)
OVERLAYS = set(CONTRACT["overlays"])
SCALES = {"tiny", "standard"}
CONTEXTS = {"internal", "client", "generic", "product"}
LIBRARY_VERSION = "1.3.0"
RUNTIMES = {"codex", "claude-code", "cline", "opencode"}
ARTIFACTS = {
    "none",
    "project-dashboard",
    "technical-dashboard",
    "management-dashboard",
    "executive-presentation",
    "sales-presentation",
    "combination",
}
PRESENTATION_PURPOSES = {"sales", "executive", "technical", "informational", "workshop", "internal"}
RESEARCH_DEPTHS = {"quick-discovery", "structured-research", "deep-research"}
EXTERNAL_RESEARCH = {"auto", "skip", "suggest"}
CAPABILITY_GAP_STRATEGIES = {"ask", "search-external", "project-local-later", "generic-only"}
EXTERNAL_SOURCE_SCOPES = {"configured", "official", "official-curated", "all"}
EXTERNAL_INTEGRATIONS = {
    "methodology-only",
    "project-local-skill",
    "project-local-agent",
    "external-tool",
    "inspiration-only",
}
EXTERNAL_RELATIONSHIPS = {"COPIED", "ADAPTED", "INSPIRED-BY", "INDEPENDENT-REIMPLEMENTATION"}
EXTERNAL_TRUST = {"OFFICIAL", "CURATED", "COMMUNITY", "UNTRUSTED"}
DIAGRAM_VIEWS = {
    "system-landscape",
    "component-architecture",
    "class",
    "er",
    "sequence",
    "data-flow",
    "migration-roadmap",
}
DIAGRAM_CONDITIONS = {
    "system-landscape": "system-landscape-view",
    "component-architecture": "component-architecture-view",
    "class": "class-model-view",
    "er": "er-data-model-view",
    "sequence": "sequence-interaction-view",
    "data-flow": "data-flow-view",
    "migration-roadmap": "migration-roadmap-view",
}
OPENSPEC_SKILLS = [
    "specify-openspec-change", "review-openspec-change", "implement-openspec-change",
    "verify-openspec-implementation", "complete-openspec-change",
]
PUBLIC_SECTOR_CONFIDENCE = {CONFIRMED, HIGH_CONFIDENCE}


def parse_scopes(value: str) -> list[str]:
    scopes = list(dict.fromkeys(part.strip().lower() for part in re.split(r"[,+]", value) if part.strip()))
    invalid = sorted(set(scopes) - SCOPES)
    if not scopes or invalid:
        raise argparse.ArgumentTypeError(f"scopes must use {sorted(SCOPES)}; invalid={invalid}")
    return list(dict.fromkeys(ARCHETYPE_ALIASES[scope] for scope in scopes))


def parse_overlays(value: str) -> list[str]:
    overlays = split_values([value])
    invalid = sorted(set(overlays) - OVERLAYS)
    if invalid:
        raise argparse.ArgumentTypeError(f"overlays must use {sorted(OVERLAYS)}; invalid={invalid}")
    return overlays


def parse_runtimes(values: list[str] | None) -> list[str]:
    runtimes = split_values(values)
    invalid = sorted(set(runtimes) - RUNTIMES)
    if invalid:
        raise ValueError(f"runtimes must use {sorted(RUNTIMES)}; invalid={invalid}")
    return runtimes


def split_people(value: str) -> list[str]:
    return list(dict.fromkeys(
        part.strip() for part in re.split(r"\s*(?:,|\+|\band\b)\s*", value, flags=re.I) if part.strip()
    ))


def labeled_value(brief: str, labels: tuple[str, ...]) -> str:
    for label in labels:
        match = re.search(rf"(?im)^\s*{re.escape(label)}\s*:\s*(.+?)\s*$", brief)
        if match:
            return match.group(1).strip()
    return ""


def infer_reference_type(source: str) -> str:
    lowered = source.lower()
    if re.match(r"^https?://", source):
        return "url"
    path = Path(source).expanduser()
    if path.exists() and path.is_dir():
        return "existing-project" if "project" in lowered or source.startswith("..") else "local-directory"
    if source.endswith("/"):
        return "local-directory"
    if re.search(r"\.(?:png|jpe?g|gif|webp|svg|pdf|pptx?|html?)$", lowered):
        return "local-file"
    if "/" in source or source.startswith("."):
        return "local-path"
    return "description"


def reference_record(value: str | dict[str, object]) -> dict[str, object]:
    if isinstance(value, dict):
        source = str(value.get("source", "")).strip()
        if not source:
            raise ValueError("reference object requires a non-empty source")
        record = dict(value)
        record["source"] = source
    else:
        raw = value.strip().lstrip("- ").strip()
        if raw.startswith("{"):
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                raise ValueError("reference JSON must be an object")
            return reference_record(parsed)
        source, intent = raw, ""
        match = re.match(r"^(.+?)\s+for\s+(.+)$", raw, re.I)
        if match:
            source, intent = match.group(1).strip(), match.group(2).strip()
        source = source.strip().strip("`\"")
        record = {"source": source}
        lowered = f" {intent.lower()} "
        applies = [name for name in (
            "timeline", "cluster", "architecture", "flow", "process", "comparison", "roadmap",
            "capability-map", "evidence-chain", "presentation", "visual-identity",
        ) if name.replace("-", " ") in lowered or name in lowered]
        uses = [name for name in (
            "structure", "density", "storytelling", "information-density", "section-transitions",
            "typography", "interaction", "navigation", "brand", "content-structure",
        ) if name.replace("-", " ") in lowered or name in lowered]
        ignores: list[str] = []
        for negative in re.findall(r"(?:not|ignore|do not copy)\s+([^.;]+)", intent, re.I):
            ignores.extend(
                item.strip().lower().replace(" ", "-")
                for item in re.split(r"\s*(?:,|\band\b)\s*", negative, flags=re.I)
                if item.strip()
            )
        if applies:
            record["applies_to"] = applies
        if uses:
            record["use"] = uses
        if ignores:
            record["ignore"] = list(dict.fromkeys(ignores))
    record.setdefault("type", infer_reference_type(str(record["source"])))
    record.setdefault("applies_to", [])
    record.setdefault("use", [])
    record.setdefault("ignore", [])
    record.setdefault("access", "read-only")
    record.setdefault("scope", "project-local")
    record.setdefault("copy_into_project", False)
    return record


def brief_references(brief: str) -> list[dict[str, object]]:
    match = re.search(r"(?ims)^\s*references?\s*:\s*(.+?)(?=^\s*[A-Za-z][A-Za-z /_-]*\s*:|\Z)", brief)
    if not match:
        return []
    values = [line.strip() for line in match.group(1).splitlines() if line.strip()]
    return [reference_record(value) for value in values]


def topic_from_brief(brief: str) -> str:
    labeled = labeled_value(brief, ("topic", "research topic", "presentation topic"))
    if labeled:
        return labeled
    match = re.search(
        r"(?is)\babout\s+(.+?)(?=\n\s*(?:audience|brand|references?|desired outcome|sales objective|source material)\s*:|[.!?]\s*$|\Z)",
        brief,
    )
    return " ".join(match.group(1).split()).strip(" .") if match else ""


def detect_runtimes(root: Path) -> dict[str, list[str]]:
    markers = {
        "codex": [root / ".codex"],
        "claude-code": [root / "CLAUDE.md", root / ".claude"],
        "cline": [root / ".cline", root / ".clinerules"],
        "opencode": [root / ".opencode", root / "opencode.json", root / "opencode.jsonc"],
    }
    evidence: dict[str, list[str]] = {}
    for runtime, paths in markers.items():
        matches = [str(path.relative_to(root)) for path in paths if path.exists()]
        if matches:
            evidence[runtime] = matches
    return evidence


def _manifest_method(text: str, section: str) -> str:
    match = re.search(
        rf"(?m)^{re.escape(section)}:\s*$\n(?:(?:  |\t).*\n)*?^\s{{2}}method:\s*['\"]?([^\s'\"]+)['\"]?\s*$",
        text,
    )
    return match.group(1) if match else ""


def detect_project_methodology(root: Path) -> dict[str, object]:
    result: dict[str, object] = {
        "specification_method": "", "specification_state": "new",
        "implementation_method": "", "evidence": [],
    }
    if not root.exists() or not root.is_dir():
        return result
    evidence: list[str] = []
    manifest = root / ".agent-commons.yaml"
    if manifest.is_file():
        text = manifest.read_text(encoding="utf-8", errors="replace")
        specification = _manifest_method(text, "specifications")
        implementation = _manifest_method(text, "implementation")
        if specification:
            result["specification_method"] = specification
            evidence.append(f".agent-commons.yaml specifications.method={specification}")
        if implementation:
            result["implementation_method"] = implementation
            evidence.append(f".agent-commons.yaml implementation.method={implementation}")
    openspec_markers = [
        root / "openspec/config.yaml", root / "openspec/specs", root / "openspec/changes",
    ]
    existing_openspec = [str(path.relative_to(root)) for path in openspec_markers if path.exists()]
    if existing_openspec:
        result["specification_method"] = "openspec"
        result["specification_state"] = "reuse"
        evidence.extend(existing_openspec)
    elif not result["specification_method"]:
        alternatives = [
            (root / ".specify", "spec-kit"),
            (root / "specifications", "project-specifications"),
            (root / "docs/specifications", "project-specifications"),
        ]
        for path, method in alternatives:
            if path.exists():
                result["specification_method"] = method
                result["specification_state"] = "preserve"
                evidence.append(str(path.relative_to(root)))
                break
    if result["specification_method"] and result["specification_method"] != "openspec":
        result["specification_state"] = "preserve"
    result["evidence"] = evidence
    return result


def _manifest_section(text: str, section: str) -> str:
    match = re.search(
        rf"(?m)^{re.escape(section)}:[ \t]*$\n(?P<body>(?:^(?:  |\t).*\n?)*)",
        text,
    )
    return match.group("body") if match else ""


def _manifest_scalar(section: str, key: str) -> str:
    match = re.search(rf"(?m)^ {{2}}{re.escape(key)}:[ \t]*(.*?)[ \t]*$", section)
    if not match:
        return ""
    value = match.group(1).strip().strip("'\"")
    return "" if value in {"", "null", "~"} else value


def _manifest_list(section: str, key: str) -> list[str]:
    match = re.search(
        rf"(?m)^ {{2}}{re.escape(key)}:[ \t]*$\n(?P<body>(?:^ {{4}}-[ \t]+.*\n?)*)",
        section,
    )
    if not match:
        return []
    return [
        item.strip().strip("'\"")
        for item in re.findall(r"(?m)^ {4}-[ \t]+(.*?)[ \t]*$", match.group("body"))
        if item.strip()
    ]


def detect_persisted_delivery(root: Path) -> dict[str, object]:
    """Read only the client and output-language fields owned by this initializer."""
    manifest = root / ".agent-commons.yaml"
    if not manifest.is_file():
        return {}
    text = manifest.read_text(encoding="utf-8", errors="replace")
    client_section = _manifest_section(text, "client")
    dashboard_section = _manifest_section(text, "dashboard")
    presentation_section = _manifest_section(text, "presentation")
    localization_section = _manifest_section(text, "localization")
    if not any((client_section, dashboard_section, presentation_section, localization_section)):
        return {}

    confidence = _manifest_scalar(client_section, "public_sector_confidence") or NOT_PUBLIC_SECTOR
    client = {
        "organization": _manifest_scalar(client_section, "organization"),
        "sector": _manifest_scalar(client_section, "sector") or "unknown",
        "public_sector": _manifest_scalar(client_section, "public_sector").lower() == "true",
        "public_sector_confidence": confidence,
        "country": _manifest_scalar(client_section, "country"),
        "locale": _manifest_scalar(client_section, "locale"),
        "evidence": ["existing .agent-commons.yaml client policy"],
    }
    dashboard_languages = _manifest_list(dashboard_section, "languages")
    presentation_languages = _manifest_list(presentation_section, "languages")
    return {
        "client": client,
        "localization": {
            "working_language": _manifest_scalar(localization_section, "working_language") or "en",
            "dashboard": _policy(
                dashboard_languages,
                _manifest_scalar(dashboard_section, "default_language"),
                _manifest_scalar(dashboard_section, "language_switch").lower() == "true",
                "existing-project-manifest",
                "language_switch",
            ),
            "presentation": _policy(
                presentation_languages,
                _manifest_scalar(presentation_section, "default_language"),
                _manifest_scalar(presentation_section, "bilingual").lower() == "true",
                "existing-project-manifest",
                "bilingual",
            ),
        },
    }


def q(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def yaml_list(lines: list[str], key: str, values: list[str], indent: int = 0) -> None:
    prefix = " " * indent
    if values:
        lines.append(f"{prefix}{key}:")
        lines.extend(f"{prefix}  - {q(value)}" for value in values)
    else:
        lines.append(f"{prefix}{key}: []")


def library_revision() -> str:
    result = subprocess.run(
        ["git", "-C", str(LIBRARY_ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def selected_composition(args: argparse.Namespace) -> dict[str, object]:
    overlays = [item for group in args.overlay for item in group]
    if args.scale == "standard" and "durable-state" not in overlays:
        overlays.append("durable-state")
    if "sales" in args.presentation_purpose and "sales-storytelling" not in overlays:
        overlays.append("sales-storytelling")
    if args.html_artifact != "none" and "branded-html" not in overlays:
        overlays.append("branded-html")
    if ("dashboard" in args.html_artifact or args.html_artifact == "combination") and "living-dashboard" not in overlays:
        overlays.append("living-dashboard")
    if args.architecture_documentation and "architecture-documentation" not in overlays:
        overlays.append("architecture-documentation")
    conditions = split_values(args.condition)
    if args.scale == "standard" and "legacy-migration" in args.scope and "source-analysis" in args.deliverable:
        if "parallel-discovery" not in conditions:
            conditions.append("parallel-discovery")
    if args.scale == "standard" and "development" in args.scope:
        if "parallel-agent-work" not in conditions:
            conditions.append("parallel-agent-work")
    if "legacy-migration" in args.scope and "requirements-extraction" in args.deliverable:
        phase_condition = (
            "migration-openspec-preparation"
            if args.migration_intent in {"preparation", "implementation"}
            else "requirements-discovery"
        )
        if phase_condition not in conditions:
            conditions.append(phase_condition)
    for view in args.diagram_view:
        condition = DIAGRAM_CONDITIONS[view]
        if condition not in conditions:
            conditions.append(condition)
    dashboard_selected = "dashboard" in args.html_artifact or args.html_artifact == "combination"
    presentation_selected = "presentation" in args.html_artifact or args.html_artifact == "combination"
    bilingual_delivery = bool(
        (dashboard_selected and args.dashboard_language_switch)
        or (presentation_selected and args.presentation_bilingual)
    )
    if bilingual_delivery and "bilingual-client-delivery" not in overlays:
        overlays.append("bilingual-client-delivery")
    if args.public_sector_applied and "public-sector-client-delivery" not in overlays:
        overlays.append("public-sector-client-delivery")
    excluded_skills: list[str] = []
    if args.specification_method != "openspec":
        excluded_skills.extend(OPENSPEC_SKILLS)
    if args.implementation_method != "test-driven-development":
        excluded_skills.append("test-driven-development")
    return resolve_composition(
        args.scope, overlays, conditions, args.scale, exclude_skills=excluded_skills,
    )


def build_initial_execution_plan(args: argparse.Namespace, external_branch: bool) -> dict[str, object]:
    if args.scale == "tiny":
        tasks = [
            {"id": "parse-brief"},
            {"id": "create-project-shell", "dependencies": ["parse-brief"], "write_paths": [".agent-commons.yaml"]},
        ]
        result = plan_execution({"schema_version": 1, "max_concurrency": 1, "tasks": tasks})
        result["policy"] = "small-single-agent"
        result["tasks"] = tasks
        return result

    tasks: list[dict[str, object]] = [
        {"id": "parse-brief"},
        {"id": "source-inspection", "dependencies": ["parse-brief"], "write_paths": ["analysis/source-inventory.json"]},
        {"id": "brand-resolution", "dependencies": ["parse-brief"], "write_paths": ["brand/profile.json"]},
        {"id": "commons-resolution", "dependencies": ["parse-brief"]},
        {"id": "environment-inspection", "dependencies": ["parse-brief"]},
        {
            "id": "initialization-fan-in",
            "dependencies": ["source-inspection", "brand-resolution", "commons-resolution", "environment-inspection"],
            "write_paths": [".agent-commons.yaml"],
        },
        {
            "id": "dashboard-shell",
            "dependencies": ["initialization-fan-in"],
            "write_paths": ["dashboard"],
        },
    ]
    if external_branch:
        tasks.append({
            "id": "external-capability-search",
            "dependencies": ["commons-resolution"],
            "write_paths": ["analysis/external-capabilities.json"],
        })
    result = plan_execution({"schema_version": 1, "max_concurrency": 4, "tasks": tasks})
    result["policy"] = "bounded-parallel"
    result["tasks"] = tasks
    result["failure_classes"] = {
        "brand-resolution": "NON_BLOCKING_USES_ACCENTURE_FALLBACK",
        "external-capability-search": "NON_BLOCKING_FOR_CORE_SETUP",
        "source-inspection": "BLOCKING_FOR_SOURCE_ANALYSIS",
    }
    return result


def infer_technology_pair(args: argparse.Namespace) -> None:
    if args.source_technology or args.target_technology:
        return
    for value in args.technology:
        match = re.match(r"^\s*(.+?)\s*(?:->|→|\bto\b)\s*(.+?)\s*$", value, re.I)
        if match:
            args.source_technology = match.group(1).strip()
            args.target_technology = match.group(2).strip()
            return


def combine_brief(args: argparse.Namespace) -> str:
    parts = [*args.brief, " ".join(args.brief_words)]
    return "\n".join(part.strip() for part in parts if part and part.strip())


def inferred_goal(profile: dict[str, object]) -> str:
    known = profile.get("known", {})
    source = known.get("source_technology")
    target = known.get("target_technology")
    deliverables = known.get("deliverables", [])
    phrases: list[str] = []
    if "source-analysis" in deliverables:
        phrases.append(f"analyze the {source} source" if source else "analyze the source system")
    if "requirements-extraction" in deliverables:
        phrases.append("derive structured requirements")
    if "migration-preparation" in deliverables:
        phrases.append(f"prepare migration to {target}" if target else "prepare the migration")
    if "migration-implementation" in deliverables:
        phrases.append(f"implement migration to {target}" if target else "implement the migration")
    if "html-dashboard" in deliverables:
        phrases.append("maintain a living HTML dashboard")
    if not phrases:
        return str(profile.get("summary") or "Define the first useful outcome with the project owner.")
    first = phrases[0][:1].upper() + phrases[0][1:]
    return first + (", " + ", ".join(phrases[1:]) if len(phrases) > 1 else "") + "."


def source_specs_from_args(args: argparse.Namespace) -> list[dict[str, object]]:
    sources: list[dict[str, object]] = []
    read_only = {str(Path(value).expanduser().resolve()) for value in args.read_only_path}
    for value in args.source:
        path = str(Path(value).expanduser().resolve())
        sources.append({
            "path": path,
            "role": "legacy-source" if "legacy-migration" in (args.scope or []) else "reference-source",
            "access": "read-only" if path in read_only else "unspecified",
        })
    for path in sorted(read_only):
        if not any(source["path"] == path for source in sources):
            sources.append({
                "path": path,
                "role": "legacy-source" if "legacy-migration" in (args.scope or []) else "reference-source",
                "access": "read-only",
            })
    return sources


def merge_brief(args: argparse.Namespace, profile: dict[str, object]) -> None:
    known = profile["known"]
    discovered = profile.get("discovered", {})
    inferred = profile["inferred"]
    methodology = known.get("methodology", {})
    args.no_openspec = bool(args.no_openspec or methodology.get("specification") == "none")
    args.no_tdd = bool(args.no_tdd or methodology.get("implementation") == "normal")
    args.explicit_openspec = bool(methodology.get("explicit_specification") and methodology.get("specification") == "openspec")
    args.explicit_tdd = bool(methodology.get("explicit_implementation") and methodology.get("implementation") == "test-driven-development")
    args.scope = args.scope or list(known["scopes"])
    args.source_technology = args.source_technology or str(
        known["source_technology"] or discovered.get("source_technology") or ""
    )
    args.target_technology = args.target_technology or str(known["target_technology"] or "")
    args.migration_intent = args.migration_intent or str(known["migration_intent"] or "")
    args.deliverable = list(dict.fromkeys([*args.deliverable, *known["deliverables"]]))
    args.technology = list(dict.fromkeys([
        *args.technology, *known["technologies"], *discovered.get("technologies", []),
    ]))
    args.html_artifact = args.html_artifact or str(known["html_artifact"] or "") or None
    args.brand_source = args.brand_source or str(known["brand_source"] or "") or None
    args.dashboard_audience = list(dict.fromkeys([*args.dashboard_audience, *known["audience"]]))
    args.dashboard_purpose = list(dict.fromkeys([*args.dashboard_purpose, *known["dashboard_purposes"]]))
    args.audience = list(dict.fromkeys([*args.audience, *known["audience"]]))
    args.research_topic = args.research_topic or str(known["research_topic"] or "")
    args.research_goal = args.research_goal or str(known["research_goal"] or "")
    args.presentation_topic = args.presentation_topic or str(known["presentation_topic"] or "")
    args.presentation_purpose = list(dict.fromkeys([
        *args.presentation_purpose, *known["presentation_purposes"],
    ]))
    args.desired_outcome = args.desired_outcome or str(known["desired_outcome"] or "")
    args.sales_objective = args.sales_objective or str(known["sales_objective"] or "")
    args.source_material = list(dict.fromkeys([*args.source_material, *known["source_material"]]))
    args.diagram_view = list(dict.fromkeys([*args.diagram_view, *known.get("diagram_views", [])]))
    known_reference_sources = {str(entry["source"]) for entry in args.references}
    for value in known["references"]:
        if value not in known_reference_sources:
            args.references.append(reference_record(str(value)))
            known_reference_sources.add(str(value))
    args.audience = list(dict.fromkeys([*args.audience, *known["audience"]]))
    args.research_topic = args.research_topic or str(known.get("research_topic") or "")
    args.research_goal = args.research_goal or str(known.get("research_goal") or "")
    args.presentation_topic = args.presentation_topic or str(known.get("presentation_topic") or "")
    args.presentation_purpose = list(dict.fromkeys([
        *args.presentation_purpose, *known.get("presentation_purposes", [])
    ]))
    args.desired_outcome = args.desired_outcome or str(known.get("desired_outcome") or "")
    args.sales_objective = args.sales_objective or str(known.get("sales_objective") or "")
    args.source_material = list(dict.fromkeys([*args.source_material, *known.get("source_material", [])]))
    profile_sources = [dict(source) for source in known["sources"]]
    explicit_sources = source_specs_from_args(args)
    merged_sources: dict[str, dict[str, object]] = {source["path"]: source for source in profile_sources}
    for source in explicit_sources:
        current = merged_sources.get(source["path"])
        if current is None or source["access"] != "unspecified":
            merged_sources[source["path"]] = source
    args.sources = list(merged_sources.values())
    args.discovered_sources = list(profile.get("discovered", {}).get("sources", []))
    args.read_only_path = list(dict.fromkeys(
        [source["path"] for source in args.sources if source["access"] == "read-only"]
    ))
    if inferred.get("evidence_traceability"):
        selected_overlays = [item for group in args.overlay for item in group]
        if "evidence-traceability" not in selected_overlays:
            args.overlay.append(["evidence-traceability"])
    args.architecture_documentation = bool(
        args.diagram_view or inferred.get("architecture_documentation") or
        "architecture-documentation" in [item for group in args.overlay for item in group]
    )
    if not args.goal:
        args.goal = inferred_goal(profile)


def _policy(
    languages: list[str],
    default_language: str,
    multiple: bool,
    source: str,
    switch_field: str,
) -> dict[str, object]:
    languages = list(dict.fromkeys(value for value in languages if value))
    if default_language and default_language not in languages:
        languages.insert(0, default_language)
    return {
        "resolved": bool(languages and default_language),
        "languages": languages,
        "default_language": default_language,
        switch_field: bool(multiple and len(languages) > 1),
        "source": source,
    }


def resolve_client_delivery(args: argparse.Namespace, profile: dict[str, object], brief: str) -> None:
    known = profile.get("known", {})
    known_client = dict(known.get("client", {}) or {})
    persisted = detect_persisted_delivery(args.root)
    persisted_client = dict(persisted.get("client", {}) or {})
    client_baseline = {**persisted_client, **{key: value for key, value in known_client.items() if value}}
    reference_urls = [
        str(entry.get("source")) for entry in args.references
        if str(entry.get("source", "")).startswith("http")
    ]
    explicit_public = True if args.public_sector_client else False if args.private_sector_client else None
    brief_has_sector_instruction = bool(re.search(
        r"\b(?:public[- ]sector|private[- ]sector|government client|public administration|"
        r"private company|not (?:a )?public[- ]sector)\b",
        brief,
        re.I,
    ))
    if explicit_public is None and persisted_client and not brief_has_sector_instruction:
        if str(persisted_client.get("public_sector_confidence")) in PUBLIC_SECTOR_CONFIDENCE:
            explicit_public = True
        elif persisted_client.get("sector") == "private":
            explicit_public = False
    client = detect_client_context(
        brief,
        reference_urls,
        brand_source=args.brand_source or "",
        organization=args.client_organization or str(client_baseline.get("organization") or ""),
        explicit_public_sector=explicit_public,
        country=args.client_country or str(client_baseline.get("country") or ""),
        locale=args.client_locale or str(client_baseline.get("locale") or ""),
    )
    args.client_organization = str(client.get("organization") or "")
    args.client_sector = str(client.get("sector") or "unknown")
    args.public_sector = bool(client.get("public_sector"))
    args.public_sector_confidence = str(client.get("public_sector_confidence") or NOT_PUBLIC_SECTOR)
    args.client_country = str(client.get("country") or "")
    args.client_locale = str(client.get("locale") or "")
    args.client_evidence = [str(value) for value in client.get("evidence", [])]
    args.public_sector_applied = args.public_sector_confidence in PUBLIC_SECTOR_CONFIDENCE and bool(args.client_locale)

    localization = dict(persisted.get("localization", {}) or {})
    known_localization = dict(known.get("localization", {}) or {})
    if known_localization.get("working_language"):
        localization["working_language"] = known_localization["working_language"]
    for output in ("dashboard", "presentation"):
        candidate = dict(known_localization.get(output, {}) or {})
        if candidate.get("resolved"):
            localization[output] = candidate
    dashboard = dict(localization.get("dashboard", {}) or {})
    presentation = dict(localization.get("presentation", {}) or {})
    defaults = public_sector_defaults(client)
    if not dashboard.get("resolved") and defaults.get("applied"):
        value = defaults["dashboard"]
        dashboard = _policy(
            list(value["languages"]), str(value["default_language"]),
            bool(value["language_switch"]), "public-sector-client-default", "language_switch",
        )
    if not presentation.get("resolved") and defaults.get("applied"):
        value = defaults["presentation"]
        presentation = _policy(
            list(value["languages"]), str(value["default_language"]),
            bool(value["bilingual"]), "public-sector-client-default", "bilingual",
        )

    working_language = args.working_language or str(localization.get("working_language") or "") or "en"
    dashboard_requested = "dashboard" in args.html_artifact or args.html_artifact == "combination"
    presentation_requested = "presentation" in args.scope or "presentation" in args.html_artifact or args.html_artifact == "combination"

    if args.client_language is not None:
        generic_default = normalize_locale(args.client_language, args.client_country)
        generic_languages = [generic_default, working_language] if args.bilingual else [generic_default]
        if dashboard_requested:
            dashboard = _policy(
                generic_languages, generic_default, bool(args.bilingual),
                "explicit-client-language", "language_switch",
            )
        if presentation_requested:
            presentation = _policy(
                generic_languages, generic_default, bool(args.bilingual),
                "explicit-client-language", "bilingual",
            )

    if args.dashboard_language:
        dashboard_languages = [normalize_locale(value, args.client_country) for value in args.dashboard_language]
        dashboard_default = normalize_locale(
            args.dashboard_default_language or dashboard_languages[0], args.client_country,
        )
        dashboard_switch = args.dashboard_language_switch
        if dashboard_switch is None:
            dashboard_switch = len(dashboard_languages) > 1
        dashboard = _policy(
            dashboard_languages, dashboard_default, dashboard_switch,
            "explicit-project-instruction", "language_switch",
        )
    elif args.dashboard_language_switch is not None and dashboard.get("resolved"):
        dashboard["language_switch"] = bool(args.dashboard_language_switch and len(dashboard.get("languages", [])) > 1)
        dashboard["source"] = "explicit-project-instruction"

    if args.presentation_language:
        presentation_languages = [normalize_locale(value, args.client_country) for value in args.presentation_language]
        presentation_default = normalize_locale(
            args.presentation_default_language or presentation_languages[0], args.client_country,
        )
        presentation_bilingual = args.presentation_bilingual
        if presentation_bilingual is None:
            presentation_bilingual = len(presentation_languages) > 1
        presentation = _policy(
            presentation_languages, presentation_default, presentation_bilingual,
            "explicit-project-instruction", "bilingual",
        )
    elif args.presentation_bilingual is not None and presentation.get("resolved"):
        presentation["bilingual"] = bool(args.presentation_bilingual and len(presentation.get("languages", [])) > 1)
        presentation["source"] = "explicit-project-instruction"

    args.working_language = working_language
    args.dashboard_languages = list(dashboard.get("languages", []))
    args.dashboard_default_language = str(dashboard.get("default_language") or "")
    args.dashboard_language_switch = bool(dashboard.get("language_switch")) if dashboard.get("resolved") else None
    args.dashboard_language_source = str(dashboard.get("source") or "unresolved")
    args.presentation_languages = list(presentation.get("languages", []))
    args.presentation_default_language = str(presentation.get("default_language") or "")
    args.presentation_bilingual = bool(presentation.get("bilingual")) if presentation.get("resolved") else None
    args.presentation_language_source = str(presentation.get("source") or "unresolved")
    args.localization_resolved = bool(
        (dashboard_requested and dashboard.get("resolved")) or
        (presentation_requested and presentation.get("resolved")) or
        (not dashboard_requested and not presentation_requested)
    )


def resolve_methodology(args: argparse.Namespace, detected: dict[str, object]) -> list[dict[str, str]]:
    scopes = args.scope or []
    implementation_scope = "development" in scopes or args.migration_intent == "implementation"
    preparation_scope = args.migration_intent == "preparation"
    default_specification = "openspec" if implementation_scope or preparation_scope else "none"
    default_implementation = "test-driven-development" if implementation_scope or preparation_scope else "none"
    existing_specification = str(detected.get("specification_method") or "")
    existing_implementation = str(detected.get("implementation_method") or "")
    conflicts: list[dict[str, str]] = []

    if args.no_openspec:
        args.specification_method = "none"
        args.specification_state = "explicit-opt-out"
    elif existing_specification and existing_specification != "openspec":
        args.specification_method = existing_specification
        args.specification_state = "preserve"
        if args.explicit_openspec:
            conflicts.append({
                "id": "specification-method-conflict",
                "detail": f"The project already uses {existing_specification}; explicit OpenSpec adoption requires a deliberate migration decision.",
            })
    else:
        args.specification_method = existing_specification or default_specification
        args.specification_state = "reuse" if existing_specification == "openspec" else "default"
    if args.specification_method != "openspec":
        args.deliverable = [value for value in args.deliverable if value != "openspec-specifications"]
    if args.specification_method == "none":
        args.dashboard_purpose = [
            value for value in args.dashboard_purpose
            if value not in {"specifications", "traceability"} or "requirements-traceability" in args.deliverable
        ]

    if args.no_tdd:
        args.implementation_method = "normal"
        args.implementation_method_state = "explicit-opt-out"
    elif existing_implementation and existing_implementation not in {"test-driven-development", "planned-test-driven-development"}:
        args.implementation_method = existing_implementation
        args.implementation_method_state = "preserve"
        if args.explicit_tdd:
            conflicts.append({
                "id": "implementation-method-conflict",
                "detail": f"The project already uses {existing_implementation}; changing to TDD requires a deliberate methodology decision.",
            })
    else:
        args.implementation_method = default_implementation
        args.implementation_method_state = "default"
    args.methodology_evidence = list(detected.get("evidence", []))
    return conflicts


def question_is_satisfied(identifier: str, args: argparse.Namespace) -> bool:
    checks = {
        "project.scope": bool(args.scope),
        "project.goal": bool(args.goal),
        "project.runtime": bool(args.runtimes),
        "sources.location": bool(args.sources),
        "migration.source_technology": bool(args.source_technology),
        "migration.target_technology": bool(args.target_technology),
        "migration.intent": bool(args.migration_intent),
        "project.deliverables": bool(args.deliverable),
        "dashboard.brand": bool(args.brand_resolved),
        "dashboard.audience": bool(args.dashboard_audience or args.audience),
        "artifact.language": bool(args.localization_resolved),
        "client.sector": bool(args.public_sector_client or args.private_sector_client or args.public_sector_confidence != "UNCERTAIN"),
        "client.locale": bool(args.client_locale),
        "research.topic": bool(args.research_topic),
        "research.goal": bool(args.research_goal or args.desired_outcome),
        "presentation.topic": bool(args.presentation_topic or args.research_topic),
        "presentation.audience": bool(args.audience),
        "presentation.purpose": bool(args.presentation_purpose),
        "presentation.outcome": bool(args.desired_outcome or args.sales_objective),
        "architecture.views": bool(args.diagram_view),
    }
    return checks.get(identifier, False)


def profile_unresolved_questions(profile: dict[str, object], args: argparse.Namespace) -> list[dict[str, object]]:
    return [question for question in profile.get("missing", []) if not question_is_satisfied(question["id"], args)]


def explicit_conflicts(args: argparse.Namespace, brief: str) -> list[dict[str, str]]:
    lower = brief.lower()
    conflicts: list[dict[str, str]] = []
    if args.read_only_path and any(token in lower for token in (
        "update the source in-place", "modify the source in-place", "change the source in-place",
        "edit the legacy source", "write to the source",
    )):
        conflicts.append({
            "id": "source-permission-conflict",
            "detail": "Explicit read-only source constraints conflict with requested in-place modification.",
        })
    if args.migration_intent == "analysis-only" and any(
        value in args.deliverable for value in ("implementation", "migration-implementation")
    ):
        conflicts.append({
            "id": "scope-conflict",
            "detail": "Analysis-only intent conflicts with an implementation deliverable.",
        })
    return conflicts


def load_accepted_external(path: Path | None) -> list[dict[str, object]]:
    if path is None:
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CapabilityGapError(f"invalid accepted external capability file: {exc}") from exc
    accepted = payload.get("accepted") if isinstance(payload, dict) else None
    if not isinstance(accepted, list):
        raise CapabilityGapError("accepted external capability file must contain an accepted list")
    required = {
        "gap_id", "candidate_id", "repository", "path", "revision", "license", "trust", "reviewed_at"
    }
    seen_gaps: set[str] = set()
    for index, entry in enumerate(accepted):
        if not isinstance(entry, dict) or not required.issubset(entry):
            raise CapabilityGapError(f"accepted[{index}] is missing required provenance fields")
        if not all(isinstance(entry[key], str) and entry[key].strip() for key in required):
            raise CapabilityGapError(f"accepted[{index}] provenance fields must be non-empty strings")
        if entry["gap_id"] in seen_gaps:
            raise CapabilityGapError(f"duplicate accepted gap_id: {entry['gap_id']}")
        seen_gaps.add(str(entry["gap_id"]))
        if entry["trust"] not in EXTERNAL_TRUST:
            raise CapabilityGapError(f"accepted[{index}] has invalid trust")
        entry.setdefault("relationship", "INSPIRED-BY")
        entry.setdefault("integration", "methodology-only")
        entry.setdefault("future_commons_candidate", False)
        if entry["relationship"] not in EXTERNAL_RELATIONSHIPS:
            raise CapabilityGapError(f"accepted[{index}] has invalid relationship")
        if entry["integration"] not in EXTERNAL_INTEGRATIONS:
            raise CapabilityGapError(f"accepted[{index}] has invalid integration")
        if not isinstance(entry["future_commons_candidate"], bool):
            raise CapabilityGapError(f"accepted[{index}] future_commons_candidate must be boolean")
    return accepted


def load_brand_profile(path: Path | None) -> dict[str, object] | None:
    if path is None:
        return None
    try:
        return validate_brand_profile(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise CapabilityGapError(f"invalid brand profile: {exc}") from exc


def resolve_gap_statuses(
    assessment: dict[str, object],
    strategy: str,
    accepted: list[dict[str, object]],
) -> list[dict[str, object]]:
    accepted_by_gap = {entry["gap_id"]: entry for entry in accepted}
    resolved: list[dict[str, object]] = []
    for gap in assessment["gaps"]:
        item = dict(gap)
        if gap["id"] in accepted_by_gap:
            item["resolution"] = "resolved-external"
            item["external_candidate"] = accepted_by_gap[gap["id"]]["candidate_id"]
        elif strategy == "project-local-later" and gap["importance"] != "optional":
            item["resolution"] = "project-local-later"
        elif strategy == "generic-only" and gap["importance"] != "optional":
            item["resolution"] = "generic-only-limitation"
        elif gap["importance"] == "optional":
            item["resolution"] = "recorded-optional"
        elif strategy in {"ask", "search-external"}:
            item["resolution"] = "external-discovery-running"
        else:
            item["resolution"] = "pending-user-choice"
        resolved.append(item)
    return resolved


def external_research_mode(args: argparse.Namespace, assessment: dict[str, object]) -> str:
    if args.external_research == "skip":
        return "skipped"
    if getattr(args, "external_discovery_reuse", None):
        return "reused"
    if automatic_external_discovery(args, assessment):
        return "running-concurrently"
    return "skipped"


def automatic_external_discovery(args: argparse.Namespace, assessment: dict[str, object]) -> bool:
    if args.scale == "tiny" or args.external_research == "skip":
        return False
    if args.external_research == "suggest":
        return True
    return bool(
        assessment["meaningful_gaps"]
        and args.capability_gap_strategy in {"ask", "search-external"}
    )


def external_discovery_state(args: argparse.Namespace, assessment: dict[str, object]) -> str:
    request_key = external_capabilities.discovery_request_key(
        [str(value) for value in assessment["search_queries"]],
        args.external_source_scope,
        LIBRARY_ROOT / "external" / "sources.yaml",
        args.external_discovery_snapshot,
    )
    state = {
        "schema_version": 2,
        "status": "running",
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "request_key": request_key,
        "gaps": [str(entry["id"]) for entry in assessment["meaningful_gaps"]],
        "queries": [str(value) for value in assessment["search_queries"]],
        "source_scope": args.external_source_scope,
        "result_path": "analysis/external-capabilities.json",
        "candidate_lifecycle": "DISCOVERED_REQUIRES_REVIEW_AND_ACCEPTANCE",
        "automatic_installation": False,
        "candidate_count": 0,
        "failures": [],
        "completed_source_tiers": [],
        "source_tiers": {},
        "safety": {"installed": False, "executed_external_code": False, "mutated_commons": False},
    }
    return json.dumps(state, indent=2, ensure_ascii=False) + "\n"


def reusable_external_discovery(
    root: Path,
    args: argparse.Namespace,
    assessment: dict[str, object],
    ttl_seconds: int = 1800,
) -> dict[str, object] | None:
    state_path = root / ".agent-commons" / "external-discovery.json"
    result_path = root / "analysis" / "external-capabilities.json"
    if not state_path.is_file():
        return None
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    expected = external_capabilities.discovery_request_key(
        [str(value) for value in assessment["search_queries"]],
        args.external_source_scope,
        LIBRARY_ROOT / "external" / "sources.yaml",
        args.external_discovery_snapshot,
    )
    if state.get("request_key") != expected:
        return None
    status = str(state.get("status", ""))
    if status == "running":
        return state if max(0.0, time.time() - state_path.stat().st_mtime) <= ttl_seconds else None
    if status not in (external_capabilities.DISCOVERY_STATUSES - {"failed"}) or not result_path.is_file():
        return None
    if max(0.0, time.time() - state_path.stat().st_mtime) > ttl_seconds:
        return None
    return state


def active_external_discovery(root: Path, ttl_seconds: int = 1800) -> dict[str, object] | None:
    lease_path = root / ".agent-commons" / "external-discovery.lock"
    if lease_path.is_file() and max(0.0, time.time() - lease_path.stat().st_mtime) <= ttl_seconds:
        try:
            lease = json.loads(lease_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            lease = {}
        return {
            "status": "running",
            "request_key": lease.get("request_key"),
            "active_lease": True,
        }
    state_path = root / ".agent-commons" / "external-discovery.json"
    if not state_path.is_file() or max(0.0, time.time() - state_path.stat().st_mtime) > ttl_seconds:
        return None
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return state if state.get("status") == "running" else None


def launch_external_discovery(
    root: Path,
    args: argparse.Namespace,
    assessment: dict[str, object],
) -> int:
    command = [
        sys.executable,
        str(LIBRARY_ROOT / "tools" / "run_external_discovery.py"),
        "--project-root", str(root),
        "--state", str(root / ".agent-commons" / "external-discovery.json"),
        "--output", str(root / "analysis" / "external-capabilities.json"),
        "--source-scope", args.external_source_scope,
        "--cache-dir", str(LIBRARY_ROOT / "external" / "cache" / "search"),
        "--lock", str(root / ".agent-commons" / "external-discovery.lock"),
    ]
    for query in assessment["search_queries"]:
        command += ["--topic", str(query)]
    for gap in assessment["meaningful_gaps"]:
        command += ["--gap", str(gap["id"])]
    if args.external_discovery_snapshot:
        command += ["--snapshot", str(args.external_discovery_snapshot)]
    process = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
        close_fds=True,
    )
    return process.pid


def yaml_capability_entries(lines: list[str], key: str, entries: list[dict[str, object]], indent: int = 2) -> None:
    prefix = " " * indent
    if not entries:
        lines.append(f"{prefix}{key}: []")
        return
    lines.append(f"{prefix}{key}:")
    for entry in entries:
        lines.append(f"{prefix}  - id: {q(str(entry['id']))}")
        lines.append(f"{prefix}    status: {entry['status']}")
        lines.append(f"{prefix}    importance: {entry['importance']}")
        lines.append(f"{prefix}    dimension: {entry['dimension']}")
        if entry.get("resolution"):
            lines.append(f"{prefix}    resolution: {entry['resolution']}")
        if entry.get("external_candidate"):
            lines.append(f"{prefix}    external_candidate: {q(str(entry['external_candidate']))}")
        yaml_list(lines, "covered_by", [str(value) for value in entry.get("covered_by", [])], indent + 4)


def yaml_external_entries(lines: list[str], entries: list[dict[str, object]]) -> None:
    if not entries:
        lines.append("  accepted: []")
        return
    lines.append("  accepted:")
    for entry in entries:
        lines += [
            f"    - gap_id: {q(str(entry['gap_id']))}",
            f"      candidate_id: {q(str(entry['candidate_id']))}",
            f"      repository: {q(str(entry['repository']))}",
            f"      path: {q(str(entry['path']))}",
            f"      revision: {q(str(entry['revision']))}",
            f"      license: {q(str(entry['license']))}",
            f"      trust: {entry['trust']}",
            f"      relationship: {entry['relationship']}",
            f"      integration: {entry['integration']}",
            "      scope: project-local",
            f"      reviewed_at: {q(str(entry['reviewed_at']))}",
            f"      future_commons_candidate: {'true' if entry['future_commons_candidate'] else 'false'}",
        ]


def yaml_reference_entries(lines: list[str], entries: list[dict[str, object]]) -> None:
    if not entries:
        lines.append("references: []")
        return
    lines.append("references:")
    for entry in entries:
        lines += [
            f"  - source: {q(str(entry['source']))}",
            f"    type: {entry['type']}",
            f"    access: {entry['access']}",
            f"    scope: {entry['scope']}",
            f"    copy_into_project: {'true' if entry['copy_into_project'] else 'false'}",
        ]
        yaml_list(lines, "applies_to", [str(value) for value in entry.get("applies_to", [])], 4)
        yaml_list(lines, "use", [str(value) for value in entry.get("use", [])], 4)
        yaml_list(lines, "ignore", [str(value) for value in entry.get("ignore", [])], 4)


def yaml_source_entries(
    lines: list[str],
    sources: list[dict[str, object]],
    discovered: list[dict[str, object]],
) -> None:
    if not sources:
        lines.append("sources: []")
        return
    discoveries = {str(entry.get("path")): entry for entry in discovered}
    lines.append("sources:")
    for source in sources:
        path = str(source["path"])
        inspection = discoveries.get(path, {})
        lines += [
            f"  - path: {q(path)}",
            f"    role: {source['role']}",
            f"    access: {source['access']}",
            f"    exists_at_initialization: {'true' if inspection.get('exists') else 'false'}",
        ]
        yaml_list(lines, "discovered_technologies", [str(value) for value in inspection.get("technologies", [])], 4)
        yaml_list(lines, "discovered_build_files", [str(value) for value in inspection.get("build_files", [])], 4)


def build_manifest(
    args: argparse.Namespace,
    composition: dict[str, object],
    assessment: dict[str, object],
    accepted: list[dict[str, object]],
) -> str:
    capabilities = composition["capabilities"]
    resolved_gaps = resolve_gap_statuses(assessment, args.capability_gap_strategy, accepted)
    accepted_gap_ids = {entry["gap_id"] for entry in accepted}
    unresolved_meaningful = [entry for entry in assessment["meaningful_gaps"] if entry["id"] not in accepted_gap_ids]
    requires_choice = False
    next_action = initial_next_action(
        scopes=args.scope,
        requirements_required="requirements-extraction" in args.deliverable,
        specification_method=args.specification_method,
        specifications_required=specifications_enabled(args) and "requirements-extraction" in args.deliverable,
        implementation_phase=implementation_phase(args),
    )
    lines = [
        "version: 1",
        "initialized_with:",
        f"  library_version: {q(LIBRARY_VERSION)}",
        f"  library_revision: {q(library_revision())}",
        "project:",
        f"  name: {q(args.name)}",
        f"  scale: {args.scale}",
        f"  context: {args.context}",
        f"  intake_mode: {args.intake_mode}",
        "  runtimes:",
        *[f"    - {runtime}" for runtime in args.runtimes],
        "  scopes:",
        *[f"    - {scope}" for scope in args.scope],
        "client:",
        f"  organization: {q(args.client_organization) if args.client_organization else 'null'}",
        f"  sector: {args.client_sector}",
        f"  public_sector: {'true' if args.public_sector else 'false'}",
        f"  public_sector_confidence: {args.public_sector_confidence}",
        f"  country: {q(args.client_country) if args.client_country else 'null'}",
        f"  locale: {q(args.client_locale) if args.client_locale else 'null'}",
    ]
    yaml_list(lines, "evidence", args.client_evidence, indent=2)
    lines += [
        "intake:",
        f"  mode: {args.intake_mode}",
        f"  brief_summary: {q(args.brief_summary) if args.brief_summary else 'null'}",
        "goal:",
        f"  outcome: {q(args.goal)}",
        "  done:",
        f"    - {q(args.done)}",
    ]
    yaml_list(lines, "deliverables", args.deliverable)
    yaml_list(lines, "technologies", args.technology)
    lines += [
        "migration:",
        f"  source_technology: {q(args.source_technology) if args.source_technology else 'null'}",
        f"  target_technology: {q(args.target_technology) if args.target_technology else 'null'}",
        f"  intent: {args.migration_intent or 'none'}",
        "requirements:",
        f"  extraction: {'true' if 'requirements-extraction' in args.deliverable else 'false'}",
        "specifications:",
        f"  method: {args.specification_method}",
        f"  state: {args.specification_state}",
        f"  generate_from_requirements: {'true' if specifications_enabled(args) and 'requirements-extraction' in args.deliverable else 'false'}",
        "implementation:",
        f"  method: {args.implementation_method}",
        f"  state: {args.implementation_method_state}",
        f"  phase: {implementation_phase(args)}",
        "lifecycle:",
        "  schema_version: 1",
        "  stage: initialized",
        "  next_action:",
        f"    capability: {next_action['capability'] or 'null'}",
        f"    subject: {q(str(next_action['subject'])) if next_action['subject'] else 'null'}",
        f"    required: {'true' if next_action['required'] else 'false'}",
        f"    reason: {q(str(next_action['reason']))}",
        "architecture_documentation:",
        f"  enabled: {'true' if args.architecture_documentation else 'false'}",
    ]
    yaml_list(lines, "views", args.diagram_view, indent=2)
    yaml_source_entries(lines, args.sources, args.discovered_sources)
    source_inventory = build_source_inventory(args) if args.discovered_sources else None
    execution = build_initial_execution_plan(args, bool(
        unresolved_meaningful and args.capability_gap_strategy in {"ask", "search-external"}
    ))
    lines += [
        "source_inventory:",
        f"  path: {q('analysis/source-inventory.json') if source_inventory else 'null'}",
        f"  fingerprint: {q(str(source_inventory['fingerprint'])) if source_inventory else 'null'}",
        f"  complete: {'true' if source_inventory and all(item['complete'] for item in source_inventory['sources']) else 'false'}",
        "execution:",
        f"  policy: {execution['policy']}",
        f"  planner: {q('tools/plan_parallel_execution.py')}",
        f"  max_concurrency: {execution['max_concurrency']}",
        f"  stage_count: {execution['stage_count']}",
        f"  parallel_stage_count: {execution['parallel_stage_count']}",
        "project_memory:",
        f"  enabled: {'true' if args.scale == 'standard' else 'false'}",
        f"  capability: {'maintain-project-memory' if args.scale == 'standard' else 'null'}",
        f"  manager_tool: {'manage-project-memory' if args.scale == 'standard' else 'null'}",
        f"  root: {q('.agent-commons/memory') if args.scale == 'standard' else 'null'}",
        f"  lazy: {'true' if args.scale == 'standard' else 'false'}",
        f"  hierarchy: {'L0-L1-L2-EVIDENCE' if args.scale == 'standard' else 'none'}",
        "  authority: canonical-evidence-before-memory",
        "  external_sharing: prohibited-unless-explicitly-authorized",
        "research:",
        f"  enabled: {'true' if 'research' in args.scope else 'false'}",
        f"  topic: {q(args.research_topic) if args.research_topic else 'null'}",
        f"  goal: {q(args.research_goal) if args.research_goal else 'null'}",
        f"  depth: {args.research_depth}",
        f"  purpose: {'presentation-input' if 'research' in args.scope and 'presentation' in args.scope else 'research-output'}",
        "presentation:",
        f"  enabled: {'true' if 'presentation' in args.scope else 'false'}",
        f"  topic: {q(args.presentation_topic) if args.presentation_topic else 'null'}",
    ]
    yaml_list(lines, "purposes", args.presentation_purpose, indent=2)
    yaml_list(lines, "audience", args.audience, indent=2)
    yaml_list(lines, "languages", args.presentation_languages, indent=2)
    lines += [
        f"  default_language: {q(args.presentation_default_language)}",
        f"  bilingual: {'true' if args.presentation_bilingual else 'false'}",
        f"  language_policy_source: {args.presentation_language_source}",
        f"  desired_outcome: {q(args.desired_outcome) if args.desired_outcome else 'null'}",
        "sales:",
        f"  enabled: {'true' if 'sales' in args.presentation_purpose else 'false'}",
        f"  objective: {q(args.sales_objective or args.desired_outcome) if (args.sales_objective or args.desired_outcome) else 'null'}",
    ]
    yaml_list(lines, "source_material", args.source_material)
    yaml_reference_entries(lines, args.references)
    lines += [
        "html:",
        f"  enabled: {'true' if args.html_artifact != 'none' else 'false'}",
        f"  purpose: {args.html_artifact}",
        f"  living: {'true' if 'dashboard' in args.html_artifact or args.html_artifact == 'combination' else 'false'}",
        "dashboard:",
        f"  enabled: {'true' if 'dashboard' in args.html_artifact or args.html_artifact == 'combination' else 'false'}",
        "  template: canonical",
        "  template_id: agent-commons-living-dashboard",
        "  structure: agent-commons-living-dashboard",
        "  structure_policy: canonical-standard-sections-with-honest-empty-states",
        "  visual_contract: agent-commons-living-dashboard-v3",
        "  fallback_policy: block-if-canonical-resources-unavailable",
        f"  show_requirements: {'true' if 'requirements-extraction' in args.deliverable else 'false'}",
        f"  show_specifications: {'true' if specifications_enabled(args) else 'false'}",
        f"  traceability: {'true' if specifications_enabled(args) or 'requirements-traceability' in args.deliverable else 'false'}",
    ]
    yaml_list(lines, "purposes", args.dashboard_purpose, indent=2)
    yaml_list(lines, "audience", args.dashboard_audience, indent=2)
    yaml_list(lines, "languages", args.dashboard_languages, indent=2)
    lines += [
        f"  default_language: {q(args.dashboard_default_language)}",
        f"  language_switch: {'true' if args.dashboard_language_switch else 'false'}",
        f"  language_policy_source: {args.dashboard_language_source}",
        "brand:",
        f"  mode: {'client' if args.brand_required else 'preset'}",
        f"  source: {q(args.brand_source)}",
        f"  status: {args.brand_status}",
        f"  required: {'true' if args.brand_required else 'false'}",
        f"  profile: {q('brand/profile.json') if args.brand_profile else 'null'}",
        f"  profile_fingerprint: {q(str(args.brand_profile['profile_fingerprint'])) if args.brand_profile else 'null'}",
        f"  theme_fingerprint: {q(str(args.brand_profile['theme_fingerprint'])) if args.brand_profile else 'null'}",
        f"  asset_fingerprint: {q(str(args.brand_profile['asset_fingerprint'])) if args.brand_profile else 'null'}",
        f"  favicon_sha256: {q(str(args.brand_profile['assets']['favicon']['sha256'])) if args.brand_profile else 'null'}",
        f"  logo_sha256: {q(str(args.brand_profile['assets']['logo']['sha256'])) if args.brand_profile else 'null'}",
        "  fidelity_gate: required-browser-computed-style-and-visible-identity",
        "localization:",
        f"  enabled: {'true' if args.localization_enabled else 'false'}",
        f"  working_language: {q(args.working_language)}",
        "  policy_precedence:",
        "    - explicit-project-instruction",
        "    - explicit-client-requirement",
        "    - public-sector-client-default",
        "    - archetype-default",
        "    - neutral-commons-default",
        "  offline: true",
        "  persistence: localStorage-with-safe-fallback",
        "external_research:",
        f"  mode: {external_research_mode(args, assessment)}",
        f"  automatic_search: {'true' if automatic_external_discovery(args, assessment) else 'false'}",
        f"  source_registry: {q('external/sources.yaml')}",
        f"  source_scope: {args.external_source_scope}",
        f"  status_path: {q('.agent-commons/external-discovery.json') if automatic_external_discovery(args, assessment) else 'null'}",
        f"  result_path: {q('analysis/external-capabilities.json') if automatic_external_discovery(args, assessment) else 'null'}",
        "composition:",
        f"  schema_version: {composition['schema_version']}",
    ]
    yaml_list(lines, "archetypes", composition["archetypes"], indent=2)
    yaml_list(lines, "overlays", composition["overlays"], indent=2)
    yaml_list(lines, "conditions", composition["conditions"], indent=2)
    yaml_list(lines, "levels", composition["levels"], indent=2)
    yaml_list(lines, "excluded_skills", composition.get("excluded_skills", []), indent=2)
    yaml_list(lines, "methodology_evidence", args.methodology_evidence)
    lines.append("commons:")
    yaml_list(lines, "skills", capabilities["skills"], indent=2)
    yaml_list(lines, "agents", capabilities["agents"], indent=2)
    yaml_list(lines, "tools", capabilities["tools"], indent=2)
    yaml_list(lines, "templates", capabilities["templates"], indent=2)
    lines += [
        "capability_state:",
        "  schema_version: 1",
        f"  strategy: {'accepted-external' if accepted else args.capability_gap_strategy}",
        f"  requires_user_choice: {'true' if requires_choice else 'false'}",
    ]
    yaml_capability_entries(lines, "covered", assessment["coverage"])
    yaml_capability_entries(lines, "gaps", resolved_gaps)
    lines.append("external_capabilities:")
    yaml_external_entries(lines, accepted)
    lines += [
        f"  discovery_status: {'reused' if getattr(args, 'external_discovery_reuse', None) else 'running' if automatic_external_discovery(args, assessment) else 'not-triggered'}",
        "  candidate_policy: review-and-explicit-acceptance-required",
        "  automatic_installation: false",
    ]
    lines.append("constraints:")
    yaml_list(lines, "source_paths_read_only", args.read_only_path, indent=2)
    yaml_list(lines, "project_rules", args.constraint, indent=2)
    yaml_list(lines, "validation", args.validation)
    lines.append("")
    return "\n".join(lines)


def bullets(values: list[str], fallback: str) -> str:
    entries = values or [fallback]
    return "\n".join(f"- {value}" for value in entries)


def gap_lines(args: argparse.Namespace, assessment: dict[str, object], accepted: list[dict[str, object]]) -> list[str]:
    resolved = resolve_gap_statuses(assessment, args.capability_gap_strategy, accepted)
    material = [entry for entry in resolved if entry["importance"] != "optional" and entry["status"] != "COVERED"]
    if not material:
        return []
    lines = ["", "## Capability gaps", ""]
    for entry in material:
        lines.append(f"- {entry['id']}: {entry['status']} ({entry['resolution']})")
    if args.capability_gap_strategy == "project-local-later":
        lines += [
            "",
            "Early task: define and validate the missing project-specific capabilities before deep analysis begins.",
        ]
    elif args.capability_gap_strategy == "generic-only":
        lines += [
            "",
            "Known limitation: technology-specific completeness is not established; generic commons methodology is the initial fallback.",
        ]
    return lines


def build_project_instructions(
    args: argparse.Namespace,
    assessment: dict[str, object],
    accepted: list[dict[str, object]],
) -> str:
    sections = [
        "# Project instructions",
        "",
        "## Objective",
        "",
        args.goal,
        "",
        "## Definition of done",
        "",
        f"- {args.done}",
        "",
        "## Scope",
        "",
        f"Project type: {', '.join(args.scope)}",
        f"Project scale: {args.scale}",
        f"Context: {args.context}",
        f"Agent runtimes: {', '.join(args.runtimes)}",
    ]
    if args.deliverable:
        sections += ["", "## Deliverables", "", bullets(args.deliverable, "")]
    if args.technology:
        sections += ["", "## Technologies", "", bullets(args.technology, "")]
    if args.source_technology or args.target_technology or args.migration_intent:
        sections += [
            "",
            "## Migration boundary",
            "",
            f"Source technology: {args.source_technology or 'unresolved'}",
            f"Target technology: {args.target_technology or 'unresolved'}",
            f"Migration intent: {args.migration_intent or 'not selected'}",
        ]
    if specifications_enabled(args) or "requirements-extraction" in args.deliverable:
        sections += [
            "",
            "## Engineering lifecycle",
            "",
            f"Requirements extraction: {'active' if 'requirements-extraction' in args.deliverable else 'not selected'}",
            f"Specifications: {args.specification_method} ({args.specification_state})",
            f"Implementation: {args.implementation_method} ({implementation_phase(args)})",
            "Keep requirement approval, specification readiness, implementation, and validation as separate states.",
        ]
        if args.specification_state == "reuse":
            sections.append("Reuse the existing OpenSpec hierarchy and configuration; do not initialize a second structure.")
        elif args.specification_state == "preserve":
            sections.append("Preserve the existing project specification method; do not replace it with OpenSpec automatically.")
        if args.implementation_method != "test-driven-development" and implementation_active(args):
            sections.append("TDD was explicitly or project-locally overridden; do not claim RED → GREEN → REFACTOR evidence.")
    if args.sources:
        sections += ["", "## Sources", ""]
        sections.extend(
            f"- {source['path']} — role: {source['role']}; access: {source['access']}"
            for source in args.sources
        )
        if any(source["access"] == "read-only" for source in args.sources):
            sections += [
                "",
                "Source repositories/directories designated read-only may be analyzed but must never be modified.",
                "All generated analysis, requirements, dashboards, and migration artifacts belong in this project, never in a read-only source.",
            ]
    if args.references:
        sources = [str(entry["source"]) for entry in args.references]
        sections += ["", "## References", "", bullets(sources, "")]
        sections += [
            "",
            "Reference intent and precedence are recorded in `.agent-commons.yaml`. Keep client and prior-project references project-local and read-only.",
        ]
    if "research" in args.scope:
        sections += [
            "",
            "## Research",
            "",
            f"Topic: {args.research_topic or 'unresolved'}",
            f"Research goal: {args.research_goal or args.desired_outcome or 'unresolved'}",
            f"Depth: {args.research_depth}",
            "Research findings are the factual basis for downstream reports or presentations; do not invent claims during presentation creation.",
        ]
    if "presentation" in args.scope:
        sections += [
            "",
            "## Presentation",
            "",
            f"Topic: {args.presentation_topic or args.research_topic or 'unresolved'}",
            f"Purposes: {', '.join(args.presentation_purpose) or 'unresolved'}",
            f"Audience: {', '.join(args.audience) or 'unresolved'}",
            f"Desired outcome: {args.desired_outcome or args.sales_objective or 'unresolved'}",
        ]
    sections += [
        "",
        "## Project-specific working rules",
        "",
        "- Inspect existing files before asking questions or editing.",
        "- Preserve user changes and keep declared source or reference inputs read-only.",
        "- Keep factual claims traceable to repository evidence.",
        "- Record exact validation and its limits at handoff.",
        "- Never store secrets, credentials, private client data, or raw logs in project memory.",
    ]
    sections.extend(f"- {rule}" for rule in args.constraint)
    sections += [
        "",
        "## Git commits",
        "",
        "- Use short, meaningful, human-readable commit messages that describe the actual change.",
        "- Do not use Conventional Commit type prefixes such as `feat:`, `fix:`, `docs:`, or `chore:`.",
        "- When the current branch contains a reliable ticket ID, prefix the message with `[TICKET-ID]`; do not invent a ticket from an ambiguous number.",
        "- Do not add `Co-authored-by` or agent-attribution trailers.",
    ]
    if args.validation:
        sections += ["", "## Required validation", "", bullets(args.validation, "")]
    if args.html_artifact != "none":
        living = "Keep it synchronized with canonical project state." if "dashboard" in args.html_artifact or args.html_artifact == "combination" else "Treat it as a presentation artifact, not canonical project state."
        sections += [
            "",
            "## HTML artifact",
            "",
            f"Purpose: {args.html_artifact}",
            f"Brand source: {args.brand_source}",
            f"Dashboard purposes: {', '.join(args.dashboard_purpose) or 'not applicable'}",
            f"Audience: {', '.join(args.dashboard_audience or args.audience) or 'unresolved'}",
            f"Working language: {args.working_language}",
            f"Dashboard languages: {', '.join(args.dashboard_languages)}; default: {args.dashboard_default_language}; switch: {'required' if args.dashboard_language_switch else 'not selected'}",
            f"Presentation languages: {', '.join(args.presentation_languages)}; default: {args.presentation_default_language}; bilingual: {'required' if args.presentation_bilingual else 'not selected'}",
            living,
        ]
        if args.dashboard_language_switch:
            sections.append("Deliver the dashboard as one offline HTML artifact; preserve filters, open sections, navigation, chart state, and scroll position while switching, and validate every language state.")
        if args.public_sector_applied:
            sections.append("Client context is public sector. Reuse client terminology and branding, keep the public-sector tone factual and restrained, and apply output-specific language policy without re-asking resolved choices.")
    sections += gap_lines(args, assessment, accepted)
    if automatic_external_discovery(args, assessment):
        sections += [
            "",
            "## External capability discovery",
            "",
            "- External capability discovery runs independently from core setup and records status under `.agent-commons/external-discovery.json`.",
            "- Never include client names, repository names, private paths, source text, or business data in external queries.",
            "- Review one promising result for license, security, and commons overlap before adopting any idea.",
            "- Discovery does not install, trust, or activate an external capability.",
        ]
    return "\n".join(sections).rstrip() + "\n"


def build_readme(
    args: argparse.Namespace,
    assessment: dict[str, object],
    accepted: list[dict[str, object]],
) -> str:
    external = ""
    if automatic_external_discovery(args, assessment):
        external = """

## External capability discovery

Agent Commons started `search-external-capabilities` concurrently with core initialization using privacy-safe
generic terms. Follow `.agent-commons/external-discovery.json`, then use `review-external-capability` for one selected result.
Search results remain inactive and must pass license, security, semantic comparison, and explicit acceptance.
"""
    gaps = ""
    material = [entry for entry in resolve_gap_statuses(assessment, args.capability_gap_strategy, accepted) if entry["importance"] != "optional"]
    if material:
        bullets_text = "\n".join(
            f"- `{entry['id']}` — {entry['status']} / {entry['resolution']}" for entry in material
        )
        follow_up = ""
        if args.capability_gap_strategy == "project-local-later":
            follow_up = "\n\nDefine and validate the missing project-specific capabilities before deep analysis begins."
        elif args.capability_gap_strategy == "generic-only":
            follow_up = "\n\nTechnology-specific completeness is not established; the project starts with generic commons methodology."
        gaps = f"""

## Capability state

{bullets_text}{follow_up}
"""
    next_action = initial_next_action(
        scopes=args.scope,
        requirements_required="requirements-extraction" in args.deliverable,
        specification_method=args.specification_method,
        specifications_required=specifications_enabled(args) and "requirements-extraction" in args.deliverable,
        implementation_phase=implementation_phase(args),
    )
    return f"""# {args.name}

## Goal

{args.goal}

## Done

- {args.done}

## Scope

{', '.join(args.scope)}

## Agent runtimes

{', '.join(args.runtimes)}

Project-specific decisions and setup belong here. Globally installed Agent Commons capabilities are
referenced from `.agent-commons.yaml`; they are not copied into this project.

## After initialization

Next action: `{next_action['command']}`

If project state changes or the next step is unclear, use `$continue-project`.
{gaps}{external}"""


def build_html(args: argparse.Namespace) -> str:
    asset = Path(__file__).resolve().parent.parent / "assets" / "project-dashboard-shell.html"
    presentation_artifact = args.html_artifact in {"executive-presentation", "sales-presentation"}
    output_locale = args.presentation_default_language if presentation_artifact else args.dashboard_default_language
    german = output_locale.startswith("de")
    not_supplied = "Nicht angegeben" if german else "Not supplied"
    not_applicable = "Nicht zutreffend" if german else "Not applicable"
    scope_labels = {
        "development": "Entwicklung", "legacy-migration": "Legacy-Modernisierung",
        "research": "Recherche", "presentation": "Präsentation",
    }
    artifact_labels = {
        "project-dashboard": "Projektdashboard", "technical-dashboard": "Technisches Dashboard",
        "management-dashboard": "Management-Dashboard", "executive-presentation": "Executive-Präsentation",
        "sales-presentation": "Vertriebspräsentation", "combination": "Dashboard und Präsentation",
    }
    migration_labels = {
        "analysis-only": "Nur Analyse", "preparation": "Migrationsvorbereitung",
        "implementation": "Migration und Umsetzung",
    }
    scope_summary = ", ".join(scope_labels.get(value, value) for value in args.scope) if german else ", ".join(args.scope)
    artifact_summary = artifact_labels.get(args.html_artifact, args.html_artifact) if german else args.html_artifact
    migration_summary = migration_labels.get(args.migration_intent, args.migration_intent) if german else args.migration_intent
    if not args.brand_profile:
        brand_summary = "Accenture-Fallback" if german else "Accenture fallback"
    else:
        brand_summary = args.brand_source
    source_summary = "; ".join(
        f"{source['path']} ({'schreibgeschützt' if german and source['access'] == 'read-only' else source['access']})"
        for source in args.sources
    ) or (args.source_technology or not_supplied)
    audience = ", ".join(args.dashboard_audience or args.audience) or not_supplied
    if "legacy-migration" in args.scope:
        empty_views = (
            ("Analyse und Nachweise", "Es werden noch keine Feststellungen behauptet. Diese Ansicht wird erst nach dokumentierter Quellenanalyse befüllt.", "Anforderungen und Migration", "Bei der Initialisierung bestehen noch keine verifizierten Kennzahlen, Risiken, Zuordnungen oder Bereitschaftsaussagen.")
            if german else
            ("Analysis & evidence", "No findings are asserted yet. Populate this view only after source evidence has been analyzed and recorded.", "Requirements & migration", "No counts, risks, mappings, or readiness claims exist at initialization. Await verified canonical project state.")
        )
    elif "development" in args.scope:
        empty_views = (
            ("Umsetzungsstatus", "Bei der Initialisierung werden weder Implementierungsfortschritt noch Qualitätskennzahlen behauptet.", "Architektur und Validierung", "Architekturentscheidungen und Testergebnisse werden erst mit kanonischen Projektnachweisen ausgewiesen.")
            if german else
            ("Delivery status", "No implementation progress or quality metrics are asserted at initialization.", "Architecture & validation", "No architectural decisions or test results are claimed until canonical project evidence exists.")
        )
    else:
        empty_views = (
            ("Nachweisbasis", "Bei der Initialisierung werden noch keine Feststellungen oder Aussagen behauptet.", "Narrativ und Entscheidungen", "Reaktionen, Entscheidungen und Lieferstatus werden erst nach Ausarbeitung und Prüfung des Artefakts ausgewiesen.")
            if german else
            ("Evidence base", "No findings or claims are asserted at initialization.", "Narrative & decisions", "No audience response, decision, or delivery status is claimed before the artifact is developed and reviewed.")
        )
    labels = ({
        "{{DOCUMENT_LANG}}": output_locale,
        "{{INITIALIZATION_CONTEXT_LABEL}}": "Initialisierungskontext",
        "{{SCOPE_LABEL}}": "Umfang",
        "{{SOURCE_SYSTEM_LABEL}}": "Quellsystem",
        "{{TARGET_SYSTEM_LABEL}}": "Zielsystem",
        "{{MIGRATION_INTENT_LABEL}}": "Migrationsziel",
        "{{AUDIENCE_LABEL}}": "Zielgruppe",
        "{{VISUAL_SOURCE_LABEL}}": "Visuelle Grundlage",
        "{{UNPOPULATED_VIEWS_LABEL}}": "Noch nicht befüllte Projektansichten",
        "{{READ_ONLY_NOTICE}}": "Diese schreibgeschützte Ansicht wird ausschließlich aus verifizierten Projektquellen befüllt. Der verbindliche Lebenszyklusstatus bleibt in den kanonischen Projektdateien.",
    } if german else {
        "{{DOCUMENT_LANG}}": output_locale or "en",
        "{{INITIALIZATION_CONTEXT_LABEL}}": "Initialization context",
        "{{SCOPE_LABEL}}": "Scope",
        "{{SOURCE_SYSTEM_LABEL}}": "Source system",
        "{{TARGET_SYSTEM_LABEL}}": "Target system",
        "{{MIGRATION_INTENT_LABEL}}": "Migration intent",
        "{{AUDIENCE_LABEL}}": "Audience",
        "{{VISUAL_SOURCE_LABEL}}": "Visual source",
        "{{UNPOPULATED_VIEWS_LABEL}}": "Unpopulated project views",
        "{{READ_ONLY_NOTICE}}": "Populate this read-only view only from verified project sources. Keep lifecycle truth in canonical project files.",
    })
    replacements = {
        "{{PROJECT_NAME}}": html.escape(args.name),
        "{{PROJECT_GOAL}}": html.escape(args.goal),
        "{{PROJECT_SCOPE}}": html.escape(scope_summary),
        "{{ARTIFACT_PURPOSE}}": html.escape(artifact_summary),
        "{{BRAND_SOURCE}}": html.escape(brand_summary),
        "{{SOURCE_SYSTEM}}": html.escape(source_summary),
        "{{TARGET_SYSTEM}}": html.escape(args.target_technology or not_supplied),
        "{{MIGRATION_INTENT}}": html.escape(migration_summary or not_applicable),
        "{{DASHBOARD_AUDIENCE}}": html.escape(audience),
        "{{PRIMARY_VIEW_TITLE}}": html.escape(empty_views[0]),
        "{{PRIMARY_VIEW_EMPTY}}": html.escape(empty_views[1]),
        "{{SECONDARY_VIEW_TITLE}}": html.escape(empty_views[2]),
        "{{SECONDARY_VIEW_EMPTY}}": html.escape(empty_views[3]),
        **{token: html.escape(value) for token, value in labels.items()},
    }
    content = asset.read_text(encoding="utf-8")
    for token, value in replacements.items():
        content = content.replace(token, value)
    if args.brand_profile:
        content = render_branded_presentation(content, args.brand_profile)
    else:
        fallback = {
            "__BRAND_ATTRIBUTES__": accenture_fallback_attributes(),
            "__BRAND_FAVICON__": accenture_fallback_favicon(),
            "__BRAND_STYLE__": accenture_fallback_css(),
            "__BRAND_LOGO__": accenture_fallback_logo("artifact-brand-logo"),
            "__BRAND_PROFILE_JSON__": json.dumps({
                "id": "accenture-fallback", "status": "fallback",
                "requested_brand_source": args.brand_source if args.brand_required else None,
                "client_brand_resolved": False,
            }, ensure_ascii=False),
        }
        for token, value in fallback.items():
            content = content.replace(token, value)
    return content


def specifications_enabled(args: argparse.Namespace) -> bool:
    return args.specification_method == "openspec"


def implementation_active(args: argparse.Namespace) -> bool:
    return "development" in args.scope or args.migration_intent == "implementation"


def implementation_phase(args: argparse.Namespace) -> str:
    if implementation_active(args):
        return "active"
    if args.migration_intent == "preparation":
        return "planned"
    return "none"


def dashboard_payload(args: argparse.Namespace) -> dict[str, object]:
    audience_values = {value.casefold() for value in (args.dashboard_audience or args.audience)}
    audience = "management" if audience_values and audience_values <= {"management", "executive", "leadership"} else "combined"
    enabled_sections: list[str] = []
    if "legacy-migration" in args.scope:
        enabled_sections += ["inventory", "dependencies", "database", "interfaces", "external-estate"]
    if "requirements-extraction" in args.deliverable:
        enabled_sections.append("requirements")
    if specifications_enabled(args):
        enabled_sections += ["requirements", "specifications", "traceability"]
    if args.architecture_documentation:
        enabled_sections.append("application-map")
    if args.migration_intent in {"preparation", "implementation"} or "development" in args.scope:
        enabled_sections += ["modernization", "application-map", "test-quality"]
    enabled_sections = list(dict.fromkeys(enabled_sections))
    next_action = initial_next_action(
        scopes=args.scope,
        requirements_required="requirements-extraction" in args.deliverable,
        specification_method=args.specification_method,
        specifications_required=specifications_enabled(args) and "requirements-extraction" in args.deliverable,
        implementation_phase=implementation_phase(args),
    )
    requested_dashboard_languages = list(args.dashboard_languages)
    localization_pending = any(locale != "en" for locale in requested_dashboard_languages)
    effective_languages = ["en"] if localization_pending else requested_dashboard_languages
    effective_default = "en" if localization_pending else args.dashboard_default_language
    subtitle = "Requirements, specifications, delivery, and evidence from canonical project state"
    dashboard_profile = (
        "legacy-modernization" if "legacy-migration" in args.scope or "legacy" in args.scope
        else "development" if "development" in args.scope
        else "research" if "research" in args.scope
        else "general"
    )
    payload: dict[str, object] = {
        "schema_version": 2,
        "title": args.name,
        "subtitle": subtitle,
        "updated_at": None,
        "audience": audience,
        "brand": "organization" if args.brand_source.lower().startswith("organization") else "project",
        "brand_requested_source": args.brand_source,
        "brand_required": args.brand_required,
        "brand_status": args.brand_status,
        "brand_fallback": "accenture" if not args.brand_profile else None,
        "brand_fallback_reason": "requested brand profile unavailable" if args.brand_required and not args.brand_profile else "no brand supplied",
        "delivery": {
            "languages": effective_languages,
            "default_language": effective_default,
            "language_switch": bool(args.dashboard_language_switch and len(effective_languages) > 1),
            "storage_key": f"{args.name}-dashboard-language",
            "requested_languages": requested_dashboard_languages,
            "requested_default_language": args.dashboard_default_language,
            "localization_status": "PENDING" if localization_pending else "NOT-REQUIRED",
        },
        "localization": {
            "messages": {
                "data.subtitle": {
                    "source": subtitle,
                    "source_hash": "sha256:" + hashlib.sha256(subtitle.encode("utf-8")).hexdigest(),
                    "translations": {
                        locale: "Anforderungen, Spezifikationen, Umsetzung und Nachweise aus dem kanonischen Projektstand"
                        for locale in args.dashboard_languages if locale.startswith("de-")
                    },
                },
            },
        },
        "openspec_required": specifications_enabled(args),
        "workflow": {
            "scopes": args.scope,
            "requirements_required": "requirements-extraction" in args.deliverable,
            "specification_method": args.specification_method,
            "specifications_required": specifications_enabled(args) and "requirements-extraction" in args.deliverable,
            "implementation_method": args.implementation_method,
            "implementation_phase": implementation_phase(args),
            "source_inventory_complete": False,
            "requires_user_choice": False,
            "dashboard_enabled": True,
        },
        "project": {
            "objective": args.goal,
            "scope": args.scope,
            "status": "Initialized; analysis not started",
            "status_detail": "No metrics, findings, risks, readiness, or delivery claims exist until canonical project evidence is recorded.",
            "next_action": next_action,
        },
        "dashboard": {
            "template": "canonical",
            "template_id": "agent-commons-living-dashboard",
            "visual_contract": "agent-commons-living-dashboard-v3",
            "mode": "full-legacy-modernization" if dashboard_profile == "legacy-modernization" else "canonical",
            "profile": dashboard_profile,
            "fallback_policy": "block-if-canonical-resources-unavailable",
            "enabled_sections": enabled_sections,
            "extensions": [],
        },
        "requirements": [], "specifications": [], "acceptance_criteria": [],
        "implementation_items": [], "tests": [], "evidence": [], "relationships": [],
    }
    if args.brand_profile:
        payload["brand_profile"] = args.brand_profile
    return payload


def build_dashboard_data(args: argparse.Namespace) -> dict[str, object]:
    return validate_dashboard(dashboard_payload(args))


def build_living_dashboard(args: argparse.Namespace) -> tuple[str, str]:
    data = build_dashboard_data(args)
    shell = (LIBRARY_ROOT / "skills/build-living-dashboard/assets/dashboard-shell.html").read_text(encoding="utf-8")
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n", render_dashboard(data, shell)


def build_research_plan(args: argparse.Namespace) -> str:
    audience = ", ".join(args.audience) or "Unresolved"
    supported = args.research_goal or args.desired_outcome or "Unresolved"
    return f"""# Research plan

## Research question

{args.research_topic or "Unresolved"}

## Audience and supported decision

- Audience: {audience}
- Decision or artifact: {supported}
- Depth: {args.research_depth}

## Scope

Record geographic, industry, technology, competitor, and temporal boundaries before broad collection.

## Evidence strategy

Prefer authoritative direct sources where appropriate. Test supporting evidence, counterarguments,
competing approaches, risks, and contradictory findings. Keep sources and supplied references read-only.

## Outputs

- `findings.md` for structured findings and implications;
- `sources.md` for relocatable provenance and evidence-quality notes;
- `synthesis.md` for the decision or downstream artifact.
"""


def build_research_synthesis(args: argparse.Namespace) -> str:
    handoff = """
## Presentation-ready handoff

- Strongest findings and quantified proof:
- Customer or client pain points:
- Implications and message hierarchy:
- Narrative direction:
- Visual and data opportunities:
- Objections and counterarguments:
- Claims that must not be made:
""" if "presentation" in args.scope else ""
    return f"""# Research synthesis

## Executive finding

## Evidence-backed findings and implications

## Conflicts, counterarguments, and risks

## Unknowns and evidence limits

## Recommended decision or next artifact
{handoff}
"""


def build_reference_readme(args: argparse.Namespace) -> str:
    lines = [
        "# Project references",
        "",
        "References guide this project only. They remain read-only, retain provenance, and never become canonical Agent Commons content automatically.",
        "",
        "Precedence: explicit project reference → project brand/design system → commons visual patterns → Accenture fallback.",
        "",
    ]
    for entry in args.references:
        lines += [
            f"## {entry['source']}",
            "",
            f"- Type: {entry['type']}",
            f"- Applies to: {', '.join(entry['applies_to']) or 'general project context'}",
            f"- Use: {', '.join(entry['use']) or 'only the explicitly relevant principles'}",
            f"- Ignore: {', '.join(entry['ignore']) or 'nothing additionally declared'}",
            "- Access: read-only",
            "- Scope: project-local",
            "",
        ]
    return "\n".join(lines).rstrip() + "\n"


def build_source_inventory(args: argparse.Namespace) -> dict[str, object]:
    artifacts: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    source_records: list[dict[str, object]] = []
    by_language: dict[str, list[str]] = {}
    for source_index, discovery in enumerate(args.discovered_sources, 1):
        source_id = f"SOURCE-{source_index:03d}"
        source_records.append({
            "id": source_id,
            "path": discovery.get("path"),
            "fingerprint": discovery.get("inventory_fingerprint"),
            "complete": bool(discovery.get("inventory_complete", False)),
            "files": len(discovery.get("artifacts", [])),
        })
        for item in discovery.get("artifacts", []):
            record = dict(item)
            record["id"] = f"{source_id}-{item['id']}"
            record["source_id"] = source_id
            artifacts.append(record)
            by_language.setdefault(str(item.get("language") or "unknown"), []).append(str(record["id"]))
        for item in discovery.get("inventory_failures", []):
            failures.append({"source_id": source_id, **item})
    batches = [
        {
            "id": f"BATCH-{index:03d}",
            "partition": language,
            "artifact_ids": sorted(ids),
            "primary_owner": f"legacy-domain:{language.casefold().replace('/', '-').replace(' ', '-')}",
        }
        for index, (language, ids) in enumerate(sorted(by_language.items()), 1)
    ]
    fingerprint_source = "\n".join(
        f"{item['id']}\t{item.get('sha256', '')}" for item in sorted(artifacts, key=lambda value: str(value["id"]))
    )
    return {
        "schema_version": 1,
        "sources": source_records,
        "fingerprint": hashlib.sha256(fingerprint_source.encode()).hexdigest(),
        "counts": {"files": len(artifacts), "failures": len(failures), "batches": len(batches)},
        "artifacts": artifacts,
        "batches": batches,
        "failures": failures,
        "reuse_contract": [
            "semantic source analysis consumes owned batch artifact IDs",
            "external capability query derivation consumes technologies and capability gaps without rescanning source",
        ],
    }


def verify_shared_brand_identity(files: dict[str, str], profile: dict[str, object] | None) -> None:
    """Fail before writing if paired HTML outputs drift from their one canonical brand profile."""
    if profile is None:
        return
    artifact_paths = [path for path in ("dashboard/index.html", "presentation/index.html") if path in files]
    for path in artifact_paths:
        content = files[path]
        for fingerprint in ("profile_fingerprint", "theme_fingerprint", "asset_fingerprint"):
            expected = str(profile[fingerprint])
            if expected not in content:
                raise CapabilityGapError(f"{path} does not contain the resolved brand {fingerprint}")
        for role in ("favicon", "logo"):
            asset_record = profile["assets"][role]
            if str(asset_record["sha256"]) not in content or str(asset_record["data_uri"]) not in content:
                raise CapabilityGapError(f"{path} does not contain the exact resolved {role} bytes and hash")


def build_files(
    args: argparse.Namespace,
    composition: dict[str, object],
    assessment: dict[str, object],
    accepted: list[dict[str, object]],
) -> dict[str, str]:
    files = {
        "AGENTS.md": build_project_instructions(args, assessment, accepted),
        ".agent-commons.yaml": build_manifest(args, composition, assessment, accepted),
        "README.md": build_readme(args, assessment, accepted),
        ".gitignore": """.env
.env.*
!.env.example
*.pem
*.key
node_modules/
.venv/
target/
build/
dist/
.idea/
.DS_Store
""",
    }
    if "claude-code" in args.runtimes:
        files["CLAUDE.md"] = "@AGENTS.md\n\n## Claude Code adapter\n\nUse the shared project context above. Runtime-specific settings belong under `.claude/`; do not duplicate the project objective here.\n"
    if "research" in args.scope:
        files["research/research-plan.md"] = build_research_plan(args)
        files["research/findings.md"] = "# Research findings\n\nRecord sourced findings, implications, counterarguments, risks, and unknowns.\n"
        files["research/sources.md"] = "# Research sources\n\nRecord stable source references, authority, freshness, and the claims each source supports.\n"
        files["research/synthesis.md"] = build_research_synthesis(args)
    if args.references:
        files["references/README.md"] = build_reference_readme(args)
    if args.discovered_sources:
        files["analysis/source-inventory.json"] = json.dumps(
            build_source_inventory(args), indent=2, ensure_ascii=False
        ) + "\n"
    if args.brand_profile:
        files["brand/profile.json"] = json.dumps(args.brand_profile, indent=2, ensure_ascii=False) + "\n"
    if args.html_artifact != "none":
        presentation = args.html_artifact in {"executive-presentation", "sales-presentation"} or (
            args.html_artifact == "combination" and args.scope == ["presentation"]
        )
        if presentation:
            files["presentation/index.html"] = build_html(args)
        elif args.html_artifact == "combination" and "presentation" in args.scope:
            files["presentation/index.html"] = build_html(args)
            dashboard_data, dashboard_html = build_living_dashboard(args)
            files["dashboard/data.json"] = dashboard_data
            files["dashboard/index.html"] = dashboard_html
        else:
            dashboard_data, dashboard_html = build_living_dashboard(args)
            files["dashboard/data.json"] = dashboard_data
            files["dashboard/index.html"] = dashboard_html
    verify_shared_brand_identity(files, args.brand_profile)
    if (
        automatic_external_discovery(args, assessment)
        and not getattr(args, "external_discovery_reuse", None)
        and not getattr(args, "external_discovery_blocked", None)
    ):
        files[".agent-commons/external-discovery.json"] = external_discovery_state(args, assessment)
    return files


def nearest_existing(path: Path) -> Path:
    candidate = path
    while not candidate.exists() and candidate != candidate.parent:
        candidate = candidate.parent
    return candidate


def inside_git(root: Path) -> bool:
    probe = nearest_existing(root)
    result = subprocess.run(
        ["git", "-C", str(probe), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def initialize_git(root: Path) -> None:
    result = subprocess.run(["git", "init", "-b", "main", str(root)], capture_output=True, text=True)
    if result.returncode != 0:
        subprocess.run(["git", "init", str(root)], check=True)


def initial_commit(root: Path, created: list[str]) -> None:
    subprocess.run(["git", "-C", str(root), "add", "--", *created], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-m", "Initialize project"], check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief_words", nargs="*", help="natural-language brief words after the options")
    parser.add_argument("--root", type=Path, help="project root; defaults to the current directory")
    parser.add_argument("--name", help="project name; defaults to the root directory name")
    parser.add_argument("--scope", type=parse_scopes, help="comma- or plus-separated archetypes; omit when --brief states them")
    parser.add_argument("--brief", action="append", default=[], help="natural-language project brief; repeat for multi-line input")
    parser.add_argument("--scale", choices=sorted(SCALES), default="standard")
    parser.add_argument("--context", choices=sorted(CONTEXTS), default="generic")
    parser.add_argument(
        "--runtime",
        action="append",
        default=[],
        help=f"agent runtime; repeat or comma-separate values from {sorted(RUNTIMES)}; omit to detect",
    )
    parser.add_argument("--goal", default="")
    parser.add_argument("--done", default="The agreed deliverables pass their explicit acceptance checks.")
    parser.add_argument("--deliverable", action="append", default=[])
    parser.add_argument("--technology", action="append", default=[])
    parser.add_argument("--source-technology", default="", help="legacy/source technology for migration capability analysis")
    parser.add_argument("--target-technology", default="", help="target technology for migration capability analysis")
    parser.add_argument("--migration-intent", choices=("analysis-only", "preparation", "implementation"), default="")
    parser.add_argument("--source", action="append", default=[], help="local source path; repeat as needed")
    parser.add_argument("--research-topic", default="")
    parser.add_argument("--research-goal", default="")
    parser.add_argument("--research-depth", choices=sorted(RESEARCH_DEPTHS), default="structured-research")
    parser.add_argument("--presentation-topic", default="")
    parser.add_argument("--presentation-purpose", action="append", choices=sorted(PRESENTATION_PURPOSES), default=[])
    parser.add_argument("--audience", action="append", default=[])
    parser.add_argument("--desired-outcome", default="")
    parser.add_argument("--sales-objective", default="")
    parser.add_argument("--source-material", action="append", default=[])
    parser.add_argument(
        "--diagram-view",
        action="append",
        choices=sorted(DIAGRAM_VIEWS),
        default=[],
        help="explicit architecture view; repeat for multiple technical diagrams",
    )
    parser.add_argument("--dashboard-audience", action="append", default=[])
    parser.add_argument("--dashboard-purpose", action="append", default=[])
    parser.add_argument("--reference", action="append", default=[], help="plain source, compact 'source for intent', or JSON reference object")
    parser.add_argument("--constraint", action="append", default=[])
    parser.add_argument("--validation", action="append", default=[])
    parser.add_argument("--html-artifact", choices=sorted(ARTIFACTS), default=None)
    parser.add_argument("--brand-source", default=None)
    parser.add_argument("--brand-profile-file", type=Path, help="resolved evidence-derived brand profile JSON")
    parser.add_argument("--client-organization", default="", help="target client organization when known")
    parser.add_argument("--client-country", default="", help="target client country, for example Austria or AT")
    parser.add_argument("--client-locale", default="", help="target client locale, for example de-AT")
    sector = parser.add_mutually_exclusive_group()
    sector.add_argument("--public-sector-client", action="store_true", help="explicitly classify the client as public sector")
    sector.add_argument("--private-sector-client", action="store_true", help="explicitly classify the client as not public sector")
    parser.add_argument("--working-language", default=None, help="internal artifact working locale, for example en")
    parser.add_argument("--client-language", default=None, help="compatibility override for the selected artifact; prefer output-specific language flags")
    parser.add_argument("--bilingual", dest="bilingual", action="store_true", help="compatibility override: retain working and client languages in the selected HTML artifact")
    parser.add_argument("--monolingual", dest="bilingual", action="store_false", help="compatibility override: deliver only the selected client language")
    parser.set_defaults(bilingual=None)
    parser.add_argument("--dashboard-language", action="append", default=[], help="dashboard locale; repeat to retain multiple locales")
    parser.add_argument("--dashboard-default-language", default="", help="dashboard initial locale")
    dashboard_switch = parser.add_mutually_exclusive_group()
    dashboard_switch.add_argument("--dashboard-language-switch", dest="dashboard_language_switch", action="store_true")
    dashboard_switch.add_argument("--no-dashboard-language-switch", dest="dashboard_language_switch", action="store_false")
    parser.set_defaults(dashboard_language_switch=None)
    parser.add_argument("--presentation-language", action="append", default=[], help="presentation locale; repeat for explicit bilingual delivery")
    parser.add_argument("--presentation-default-language", default="", help="presentation initial locale")
    presentation_language = parser.add_mutually_exclusive_group()
    presentation_language.add_argument("--presentation-bilingual", dest="presentation_bilingual", action="store_true")
    presentation_language.add_argument("--presentation-monolingual", dest="presentation_bilingual", action="store_false")
    parser.set_defaults(presentation_bilingual=None)
    parser.add_argument(
        "--external-research",
        choices=sorted(EXTERNAL_RESEARCH),
        default="auto",
        help="auto starts non-blocking discovery for material capability gaps; suggest explicitly starts it; skip disables it",
    )
    parser.add_argument(
        "--capability-gap-strategy",
        choices=sorted(CAPABILITY_GAP_STRATEGIES),
        default="ask",
        help="how material gaps are handled; ask/search-external start discovery without blocking core setup",
    )
    parser.add_argument(
        "--external-source-scope",
        choices=sorted(EXTERNAL_SOURCE_SCOPES),
        default="configured",
        help="source boundary for an explicitly requested external search handoff",
    )
    parser.add_argument(
        "--accepted-external-file",
        type=Path,
        help="JSON provenance for user-selected external findings; records project-local acceptance only",
    )
    parser.add_argument(
        "--external-discovery-snapshot",
        type=Path,
        help="deterministic offline GitHub snapshot for evaluation or disconnected initialization",
    )
    parser.add_argument(
        "--overlay",
        action="append",
        type=parse_overlays,
        default=[],
        help=f"explicit overlay; repeat or comma-separate values from {sorted(OVERLAYS)}",
    )
    parser.add_argument(
        "--condition",
        action="append",
        default=[],
        help="explicit archetype condition id to activate; repeat or comma-separate",
    )
    parser.add_argument("--read-only-path", action="append", default=[], help="source/reference path the project must not modify")
    parser.add_argument("--no-openspec", action="store_true", help="explicitly opt out of the default OpenSpec specification method")
    parser.add_argument("--no-tdd", action="store_true", help="explicitly opt out of the default test-driven implementation method")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-git", action="store_true")
    parser.add_argument("--initial-commit", action="store_true", help="commit only when this run creates a new Git repository")
    args = parser.parse_args()
    args.explicit_openspec = False
    args.explicit_tdd = False
    args.localization_resolved = bool(
        args.client_language is not None or args.bilingual is not None or
        args.dashboard_language or args.dashboard_default_language or args.dashboard_language_switch is not None or
        args.presentation_language or args.presentation_default_language or args.presentation_bilingual is not None
    )

    root = (args.root or Path.cwd()).expanduser().resolve()
    args.root = root
    args.name = args.name or root.name
    if root == Path("/") or root == Path.home().resolve():
        parser.error("refusing to initialize a filesystem or home-directory root")

    brief = combine_brief(args)
    args.intake_mode = "brief-driven" if brief else ("structured" if args.scope else "interactive")
    profile = parse_brief(brief, Path.cwd()) if brief else {
        "schema_version": 1,
        "mode": args.intake_mode,
        "summary": "",
        "known": {
            "scopes": [], "source_technology": None, "target_technology": None, "sources": [],
            "deliverables": [], "html_artifact": None, "brand_source": None, "audience": [],
            "client": {
                "organization": None, "sector": "unknown", "public_sector": False,
                "public_sector_confidence": "NOT_PUBLIC_SECTOR", "country": None,
                "locale": None, "evidence": [],
            },
            "dashboard_purposes": [], "migration_intent": None, "technologies": [], "references": [],
            "research_topic": None, "research_goal": None, "presentation_topic": None,
            "presentation_purposes": [], "desired_outcome": None, "sales_objective": None,
            "source_material": [], "diagram_views": [],
            "methodology": {
                "specification": None, "implementation": None,
                "explicit_specification": False, "explicit_implementation": False,
            },
            "localization": {
                "resolved": False, "working_language": None,
                "dashboard": {
                    "resolved": False, "languages": [], "default_language": None,
                    "language_switch": False, "source": "unresolved",
                },
                "presentation": {
                    "resolved": False, "languages": [], "default_language": None,
                    "bilingual": False, "source": "unresolved",
                },
            },
        },
        "discovered": {"sources": []},
        "inferred": {},
        "missing": interactive_questions() if args.intake_mode == "interactive" else [],
        "conflicts": [],
    }
    args.brief_summary = str(profile.get("summary") or "")
    if args.intake_mode == "interactive":
        interactive_runtime_evidence = detect_runtimes(root)
        questions = [
            item for item in interactive_questions()
            if item["id"] != "project.runtime" or not interactive_runtime_evidence
        ]
        plan = {
            "root": str(root),
            "mode": "interactive",
            "intake": profile,
            "runtime_evidence": interactive_runtime_evidence,
            "questions": questions,
            "conflicts": [],
            "create": [],
            "skip_existing": [],
            "initialize_git": False,
            "stopped_before_changes": True,
        }
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        return 0
    raw_references = [*args.reference]
    try:
        args.references = [reference_record(value) for value in raw_references]
        args.references.extend(brief_references(brief))
    except (ValueError, json.JSONDecodeError) as exc:
        parser.error(f"invalid reference: {exc}")
    deduplicated_references: dict[str, dict[str, object]] = {}
    for entry in args.references:
        deduplicated_references[str(entry["source"])] = entry
    args.references = list(deduplicated_references.values())
    if brief:
        merge_brief(args, profile)
    else:
        args.sources = source_specs_from_args(args)
        args.discovered_sources = []
        args.architecture_documentation = bool(
            args.diagram_view or "architecture-documentation" in [item for group in args.overlay for item in group]
        )
    args.brand_resolved = args.brand_source is not None
    if args.scope:
        args.scope = list(dict.fromkeys(ARCHETYPE_ALIASES.get(scope, scope) for scope in args.scope))
    if args.html_artifact is None:
        if "presentation" in (args.scope or []) and "sales" in args.presentation_purpose:
            args.html_artifact = "sales-presentation"
        elif "presentation" in (args.scope or []) and "executive" in args.presentation_purpose:
            args.html_artifact = "executive-presentation"
        else:
            args.html_artifact = "none"
    args.goal = args.goal or str(profile.get("summary") or "Define the first useful outcome with the project owner.")

    resolve_client_delivery(args, profile, brief)

    try:
        args.runtimes = parse_runtimes(args.runtime)
    except ValueError as exc:
        parser.error(str(exc))
    runtime_evidence = detect_runtimes(root)
    if not args.runtimes:
        args.runtimes = list(runtime_evidence)
    if not args.runtimes and args.intake_mode == "structured":
        parser.error(f"runtime could not be detected; pass one or more --runtime values from {sorted(RUNTIMES)}")

    intake_questions = profile_unresolved_questions(profile, args)
    question_catalog = {item["id"]: item for item in interactive_questions()}
    question_catalog.update({
        "client.sector": {
            "id": "client.sector",
            "prompt": "Is this organization a public-sector client?",
            "options": ["Yes", "No"],
        },
        "client.locale": {
            "id": "client.locale",
            "prompt": "Which client locale should govern delivery?",
            "options": ["German (Austria)", "German (Germany)", "German (Switzerland)", "Other"],
        },
    })
    if (
        args.html_artifact != "none"
        and args.public_sector_confidence == "UNCERTAIN"
        and not any(item["id"] == "client.sector" for item in intake_questions)
    ):
        intake_questions.append(question_catalog["client.sector"])
    elif (
        args.html_artifact != "none"
        and args.public_sector_confidence in PUBLIC_SECTOR_CONFIDENCE
        and not args.client_locale
        and not any(item["id"] == "client.locale" for item in intake_questions)
    ):
        intake_questions.append(question_catalog["client.locale"])
    if not args.runtimes and not any(item["id"] == "project.runtime" for item in intake_questions):
        intake_questions.append(question_catalog["project.runtime"])
    detected_methodology = detect_project_methodology(root)
    methodology_conflicts = resolve_methodology(args, detected_methodology)
    methodology_plan = {
        "specification": args.specification_method,
        "specification_state": args.specification_state,
        "implementation": args.implementation_method,
        "implementation_state": args.implementation_method_state,
        "phase": implementation_phase(args),
        "evidence": args.methodology_evidence,
    }
    conflicts = [
        *profile.get("conflicts", []), *explicit_conflicts(args, brief), *methodology_conflicts,
    ]
    unique_conflicts = {str(item["id"]): item for item in conflicts}
    conflicts = list(unique_conflicts.values())

    if not args.scope or not args.runtimes:
        plan = {
            "root": str(root),
            "mode": args.intake_mode,
            "intake": profile,
            "questions": intake_questions,
            "conflicts": conflicts,
            "create": [],
            "skip_existing": [],
            "methodology": methodology_plan,
            "initialize_git": False,
            "stopped_before_changes": True,
        }
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        return 0

    if not args.dashboard_languages:
        args.dashboard_languages = ["en"]
        args.dashboard_default_language = "en"
        args.dashboard_language_switch = False
        args.dashboard_language_source = "neutral-commons-default"
    if not args.presentation_languages:
        args.presentation_languages = ["en"]
        args.presentation_default_language = "en"
        args.presentation_bilingual = False
        args.presentation_language_source = "neutral-commons-default"
    dashboard_selected = "dashboard" in args.html_artifact or args.html_artifact == "combination"
    presentation_selected = "presentation" in args.html_artifact or args.html_artifact == "combination"
    args.localization_enabled = bool(
        (dashboard_selected and (args.dashboard_language_switch or args.dashboard_default_language != "en"))
        or (presentation_selected and (args.presentation_bilingual or args.presentation_default_language != "en"))
    )
    args.brand_source = args.brand_source or "neutral-premium"
    try:
        args.brand_profile = load_brand_profile(args.brand_profile_file)
    except CapabilityGapError as exc:
        parser.error(str(exc))
    args.brand_required = bool(
        args.brand_source.startswith(("http://", "https://"))
        or args.brand_source not in {"neutral-premium", "organization", "project"}
    )
    args.brand_status = "resolved" if args.brand_profile else "fallback"
    if args.brand_profile:
        profile_locator = str(args.brand_profile["source"]["requested_url"])
        if args.brand_source.startswith(("http://", "https://")) and profile_locator != args.brand_source:
            parser.error("brand profile source locator does not match the supplied brand source")

    try:
        infer_technology_pair(args)
        composition = selected_composition(args)
        assessment = assess_capability_gaps(
            composition,
            source=args.source_technology,
            target=args.target_technology,
            goal=args.goal,
            deliverables=args.deliverable,
            validation=args.validation,
        )
        accepted = load_accepted_external(args.accepted_external_file)
        known_gap_ids = {entry["id"] for entry in assessment["gaps"]}
        unknown_accepted = sorted(str(entry["gap_id"]) for entry in accepted if entry["gap_id"] not in known_gap_ids)
        if unknown_accepted:
            raise CapabilityGapError(f"accepted external findings reference unknown gaps: {unknown_accepted}")
        discovery_enabled = automatic_external_discovery(args, assessment)
        args.external_discovery_reuse = reusable_external_discovery(root, args, assessment) if discovery_enabled else None
        args.external_discovery_blocked = active_external_discovery(root) if discovery_enabled and not args.external_discovery_reuse else None
        files = build_files(args, composition, assessment, accepted)
    except (CompositionError, CapabilityGapError) as exc:
        parser.error(str(exc))
    accepted_gap_ids = {entry["gap_id"] for entry in accepted}
    unresolved_meaningful = [
        entry for entry in assessment["meaningful_gaps"] if entry["id"] not in accepted_gap_ids
    ]
    discovery_requested = automatic_external_discovery(args, assessment)
    search_handoff = bool(discovery_requested)
    choice_required = False
    intake_required = bool(intake_questions or conflicts)
    stopped_before_changes = intake_required
    create = [] if stopped_before_changes else [relative for relative in files if not (root / relative).exists()]
    skip = [relative for relative in files if (root / relative).exists()]
    init_git = not stopped_before_changes and not args.no_git and not inside_git(root)
    plan = {
        "root": str(root),
        "mode": args.intake_mode,
        "intake": profile,
        "runtimes": args.runtimes,
        "runtime_evidence": runtime_evidence,
        "methodology": methodology_plan,
        "composition": composition,
        "create": create,
        "skip_existing": skip,
        "initialize_git": init_git,
        "initial_commit": bool(args.initial_commit and init_git),
        "capability_assessment": assessment,
        "capability_gap_strategy": args.capability_gap_strategy,
        "choice_required": choice_required,
        "choices": ["search-external", "project-local-later", "generic-only"] if choice_required else [],
        "external_research": external_research_mode(args, assessment),
        "external_source_scope": args.external_source_scope,
        "search_handoff": {
            "workflow": "search-external-capabilities",
            "queries": assessment["search_queries"],
            "stop_after_findings": True,
            "requires_explicit_candidate_acceptance": True,
        } if search_handoff else None,
        "automatic_external_search": discovery_requested,
        "external_discovery": {
            "status": str((args.external_discovery_reuse or args.external_discovery_blocked or {}).get("status", "running")),
            "state_path": ".agent-commons/external-discovery.json",
            "result_path": "analysis/external-capabilities.json",
            "reused": bool(args.external_discovery_reuse),
            "blocked_by_active_run": bool(args.external_discovery_blocked),
        } if discovery_requested else {"status": "not-triggered"},
        "accepted_external_candidates": [entry["candidate_id"] for entry in accepted],
        "execution_plan": build_initial_execution_plan(args, discovery_requested),
        "safe_initialization_continues": not intake_required,
        "capability_dependent_work_blocked": False,
        "brand_delivery_blocked": False,
        "brand_fallback_applied": bool(not args.brand_profile),
        "stopped_before_changes": stopped_before_changes,
        "questions": intake_questions,
        "conflicts": conflicts,
        "inferred": {
            "scopes": args.scope,
            "research_topic": args.research_topic or None,
            "presentation_topic": args.presentation_topic or None,
            "presentation_purposes": args.presentation_purpose,
            "audience": args.audience,
            "brand_source": args.brand_source if args.brand_resolved else None,
            "client": {
                "organization": args.client_organization or None,
                "sector": args.client_sector,
                "public_sector": args.public_sector,
                "public_sector_confidence": args.public_sector_confidence,
                "country": args.client_country or None,
                "locale": args.client_locale or None,
            },
            "reference_count": len(args.references),
            "diagram_views": args.diagram_view,
            "working_language": args.working_language,
            "dashboard_languages": args.dashboard_languages if args.dashboard_languages else None,
            "dashboard_default_language": args.dashboard_default_language or None,
            "dashboard_language_switch": args.dashboard_language_switch,
            "presentation_languages": args.presentation_languages if args.presentation_languages else None,
            "presentation_default_language": args.presentation_default_language or None,
            "presentation_bilingual": args.presentation_bilingual,
            "specification_method": args.specification_method,
            "implementation_method": args.implementation_method,
        },
        "brief_profile": profile,
        "unresolved_questions": intake_questions,
        "optional_questions": [] if args.references or not ("presentation" in args.scope or args.html_artifact != "none") else [
            "Do you have screenshots, decks, diagrams, timelines, cluster examples, websites, brand material, or existing projects that should guide the visual work?"
        ],
    }
    plan["next_action"] = initial_next_action(
        scopes=args.scope,
        requirements_required="requirements-extraction" in args.deliverable,
        specification_method=args.specification_method,
        specifications_required=specifications_enabled(args) and "requirements-extraction" in args.deliverable,
        implementation_phase=implementation_phase(args),
    )
    if args.dry_run or stopped_before_changes:
        plan["result"] = "preview" if args.dry_run else "stopped-before-changes"
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        return 0

    root.mkdir(parents=True, exist_ok=True)
    for relative in create:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(files[relative], encoding="utf-8")
    if discovery_requested and not args.external_discovery_reuse and not args.external_discovery_blocked:
        plan["external_discovery"]["pid"] = launch_external_discovery(root, args, assessment)
    if init_git:
        initialize_git(root)
    if args.initial_commit and init_git and create:
        initial_commit(root, create)
    plan["result"] = "initialized"
    plan["message"] = "Project initialized."
    print(json.dumps(plan, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
