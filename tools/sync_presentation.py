#!/usr/bin/env python3
"""Synchronize and validate presentation data from canonical Agent Commons metadata."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "install"))
from skill_catalog import SkillCatalogError, discover_canonical_skills


ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "catalog" / "capabilities.yaml"
VERSION_PATH = ROOT / "VERSION"
PRESENTATION_PATH = ROOT / "presentation" / "index.html"
DATA_PATH = ROOT / "presentation" / "assets" / "library-data.js"
STANDALONE_PATH = ROOT / "presentation" / "agent-commons.html"
DATA_SCRIPT_RE = re.compile(
    r'(?P<indent>[ \t]*)<script\s+src=["\']assets/library-data\.js["\']\s*></script>'
)
START = '  <script type="application/json" id="capability-data">\n'
END = '\n  </script><!-- capability-data:end -->'
MAX_SOURCE_PREVIEW = 2400
GENERATED_HEADER = """// AUTO-GENERATED. DO NOT EDIT DIRECTLY.
// Run: python3 tools/refresh_commons_presentation.py
window.AGENT_COMMONS_DATA = """
GENERATED_SUFFIX = ";\n"
VALID_TYPES = {"skill", "agent", "tool", "template", "archetype", "overlay", "adapter", "eval", "external"}


class PresentationSyncError(ValueError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PresentationSyncError(f"invalid canonical JSON/YAML: {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise PresentationSyncError(f"canonical object must be a mapping: {path.relative_to(ROOT)}")
    return value


def list_of_strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def humanize(identifier: str) -> str:
    special = {
        "adm": "ADM", "c4": "C4", "dfd": "DFD", "er": "ER", "html": "HTML",
        "mcp": "MCP", "openspec": "OpenSpec", "oss": "OSS", "tdd": "TDD", "uml": "UML",
    }
    return " ".join(special.get(word, word.capitalize()) for word in identifier.replace("_", "-").split("-") if word)


def sanitize_preview(text: str) -> str:
    text = re.sub(r"/Users/[^\s'\"`]+", "<local-path>", text)
    text = re.sub(r"(?i)[A-Z]:\\\\Users\\\\[^\s'\"`]+", "<local-path>", text)
    text = re.sub(r"(?<![\w.-])/(?:home|private|Volumes)/[^\s'\"`]+", "<local-path>", text)
    text = re.sub(r"(?im)^\s*(?:token|api[_-]?key|secret|password)\s*[:=].*$", "[redacted]", text)
    text = text.strip()
    if len(text) <= MAX_SOURCE_PREVIEW:
        return text
    clipped = text[:MAX_SOURCE_PREVIEW].rsplit("\n", 1)[0].rstrip()
    return f"{clipped}\n… preview truncated"


def markdown_frontmatter(text: str, path: Path) -> dict[str, str]:
    match = re.match(r"---\n(?P<frontmatter>.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise PresentationSyncError(f"missing frontmatter: {path.relative_to(ROOT)}")
    result: dict[str, str] = {}
    for line in match.group("frontmatter").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def markdown_headings(text: str) -> list[str]:
    return [match.group(1).strip() for match in re.finditer(r"(?m)^#{2,3}\s+(.+?)\s*$", text)]


def description_parts(description: str) -> tuple[str, list[str], list[str]]:
    use_match = re.search(r"(?:^|\.\s+)Use\s+(.+?)(?=\.\s+(?:Do not use|Prefer|$)|\.$)", description)
    avoid_match = re.search(r"(?:^|\.\s+)Do not use\s+(.+?)(?=\.$)", description)
    purpose = description
    if use_match:
        purpose = description[: use_match.start()].strip().rstrip(".")
    return (
        purpose or description,
        [use_match.group(1).strip()] if use_match else [],
        [avoid_match.group(1).strip()] if avoid_match else [],
    )


def python_summary(path: Path, text: str) -> str:
    try:
        value = ast.get_docstring(ast.parse(text))
    except SyntaxError:
        value = None
    if value:
        return value.strip().split("\n\n", 1)[0]
    return f"Deterministic tool implemented by {path.name}."


def text_summary(path: Path, text: str) -> str:
    if path.suffix == ".py":
        return python_summary(path, text)
    heading = re.search(r"(?m)^#\s+(.+)$", text)
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    for paragraph in paragraphs:
        if paragraph.startswith(("#", "---", "```", "{")):
            continue
        return re.sub(r"\s+", " ", paragraph)[:420]
    return heading.group(1).strip() if heading else f"Reusable {path.suffix.lstrip('.') or 'text'} artifact."


def base_node(
    *,
    identifier: str,
    kind: str,
    path: Path,
    name: str,
    description: str,
    purpose: str | None = None,
    use_when: Iterable[str] = (),
    not_when: Iterable[str] = (),
    inputs: Iterable[str] = (),
    workflow: Iterable[str] = (),
    outputs: Iterable[str] = (),
    validation: Iterable[str] = (),
    tags: Iterable[str] = (),
    search_terms: Iterable[str] = (),
    runtime_support: Iterable[str] = (),
    source_text: str | None = None,
) -> dict[str, object]:
    relative = path.relative_to(ROOT).as_posix()
    clean = lambda value: sanitize_preview(str(value))
    clean_list = lambda values: [clean(value) for value in values if value]
    return {
        "key": f"{kind}:{identifier}",
        "id": identifier,
        "name": name,
        "type": kind,
        "path": relative,
        "description": clean(description.strip()),
        "purpose": clean((purpose or description).strip()),
        "use_when": clean_list(use_when),
        "not_when": clean_list(not_when),
        "inputs": clean_list(inputs),
        "workflow": clean_list(workflow),
        "outputs": clean_list(outputs),
        "validation": clean_list(validation),
        "tags": sorted(set(clean_list(tags))),
        "search_terms": sorted(set(clean_list(search_terms)), key=lambda term: (term.lower(), term)),
        "runtime_support": clean_list(runtime_support),
        "source_preview": sanitize_preview(source_text if source_text is not None else path.read_text(encoding="utf-8")),
    }


def capability_refs(value: object) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    if not isinstance(value, dict):
        return refs
    for kind in ("skills", "agents", "tools", "templates"):
        for identifier in list_of_strings(value.get(kind, [])):
            refs.append((kind[:-1], identifier))
    for level in ("required", "default", "recommended", "optional"):
        group = value.get(level, {})
        if not isinstance(group, dict):
            continue
        for kind in ("skills", "agents", "tools", "templates"):
            for identifier in list_of_strings(group.get(kind, [])):
                refs.append((kind[:-1], identifier))
    return refs


def all_composition_refs(data: dict[str, Any]) -> list[tuple[str, str]]:
    refs = capability_refs(data.get("capabilities"))
    for condition in data.get("conditions", []):
        if isinstance(condition, dict):
            refs.extend(capability_refs(condition.get("capabilities")))
    return refs


def eval_identifiers(path: Path, root_key: str) -> list[str]:
    text = path.read_text(encoding="utf-8")
    inside = False
    identifiers: list[str] = []
    for line in text.splitlines():
        if re.fullmatch(rf"{re.escape(root_key)}:\s*", line):
            inside = True
            continue
        if inside and line and not line.startswith(" "):
            break
        match = re.match(r"^  ([a-z0-9][a-z0-9-]+):\s*$", line) if inside else None
        if match:
            identifiers.append(match.group(1))
    return identifiers


def add_edge(
    edges: list[dict[str, str]],
    seen: set[tuple[str, str, str]],
    source: str,
    target: str,
    relationship: str,
    evidence: str,
) -> None:
    marker = (source, target, relationship)
    if marker in seen:
        return
    seen.add(marker)
    edges.append({"source": source, "target": target, "relationship": relationship, "evidence": evidence})


def build_payload() -> dict[str, object]:
    catalog = read_json(CATALOG_PATH)
    adapters_data = [(path, read_json(path)) for path in sorted((ROOT / "adapters").glob("*/adapter.yaml"))]
    adapter_names = [str(data.get("display_name", humanize(str(data.get("id", path.parent.name))))) for path, data in adapters_data]
    nodes: list[dict[str, object]] = []
    edges: list[dict[str, str]] = []
    edge_seen: set[tuple[str, str, str]] = set()

    skills = catalog.get("skills")
    if not isinstance(skills, dict):
        raise PresentationSyncError("catalog skills must be an object")
    try:
        canonical_skills = discover_canonical_skills(ROOT, check_workstation_paths=False)
    except SkillCatalogError as exc:
        raise PresentationSyncError(str(exc)) from exc
    skill_paths = [skill.skill_file for skill in canonical_skills]
    skill_ids = {skill.canonical_id for skill in canonical_skills}
    skill_by_id = {skill.canonical_id: skill for skill in canonical_skills}
    declared_skill_names: dict[str, Path] = {}
    for identifier, entry in sorted(skills.items()):
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise PresentationSyncError(f"invalid skill catalog entry: {identifier}")
        if not (ROOT / entry["path"]).is_file():
            raise PresentationSyncError(f"broken skill source path: {entry['path']}")
    for path in skill_paths:
        identifier = path.parent.name
        entry = skills.get(identifier, {})
        if not isinstance(entry, dict):
            raise PresentationSyncError(f"invalid skill catalog entry: {identifier}")
        text = path.read_text(encoding="utf-8")
        canonical_skill = skill_by_id[identifier]
        declared_name = canonical_skill.name
        if declared_name in declared_skill_names:
            other = declared_skill_names[declared_name]
            raise PresentationSyncError(
                f"duplicate skill ID {declared_name}: {other.relative_to(ROOT)} and {path.relative_to(ROOT)}"
            )
        declared_skill_names[declared_name] = path
        if declared_name != identifier:
            raise PresentationSyncError(f"skill ID does not match directory: {path.relative_to(ROOT)}")
        description = canonical_skill.description
        if not description:
            raise PresentationSyncError(f"missing description: {path.relative_to(ROOT)}")
        purpose, use_when, not_when = description_parts(description)
        related = list_of_strings(entry.get("related", []))
        if any(item not in skill_ids for item in related):
            raise PresentationSyncError(f"invalid related skill reference: {identifier}")
        for field in ("provides", "keywords", "inputs", "outputs"):
            values = entry.get(field, [])
            if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
                raise PresentationSyncError(f"invalid {field} metadata: {identifier}")
        nodes.append(
            base_node(
                identifier=identifier,
                kind="skill",
                path=path,
                name=humanize(canonical_skill.name),
                description=description,
                purpose=purpose,
                use_when=use_when,
                not_when=not_when,
                inputs=list_of_strings(entry.get("inputs", [])),
                workflow=markdown_headings(text),
                outputs=list_of_strings(entry.get("outputs", [])),
                tags=list_of_strings(entry.get("provides", [])) + list_of_strings(entry.get("keywords", [])),
                search_terms=[identifier, humanize(identifier)]
                + list_of_strings(entry.get("aliases", []))
                + list_of_strings(entry.get("provides", []))
                + list_of_strings(entry.get("keywords", [])),
                runtime_support=adapter_names,
                source_text=text,
            )
        )
        for related_id in related:
            add_edge(edges, edge_seen, f"skill:{identifier}", f"skill:{related_id}", "works with", "catalog/capabilities.yaml related")

    catalog_agents = catalog.get("agents", {})
    if not isinstance(catalog_agents, dict):
        raise PresentationSyncError("catalog agents must be an object")
    agent_entries: dict[str, dict[str, object]] = {}
    catalog_agent_by_path: dict[str, tuple[str, dict[str, object]]] = {}
    for identifier, entry in catalog_agents.items():
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise PresentationSyncError(f"invalid agent catalog entry: {identifier}")
        catalog_agent_by_path[str(entry["path"])] = (identifier, entry)
    for path in sorted((ROOT / "agents").glob("*.yaml")):
        relative = path.relative_to(ROOT).as_posix()
        identifier, entry = catalog_agent_by_path.get(relative, (path.stem, {}))
        if identifier in agent_entries:
            raise PresentationSyncError(f"duplicate agent ID: {identifier}")
        agent_entries[identifier] = {**entry, "path": relative}
    for identifier, entry in catalog_agents.items():
        if identifier not in agent_entries:
            raise PresentationSyncError(f"broken agent source path: {entry['path']}")

    catalog_tools = catalog.get("tools", {})
    if not isinstance(catalog_tools, dict):
        raise PresentationSyncError("catalog tools must be an object")
    tool_entries: dict[str, dict[str, object]] = {identifier: dict(entry) for identifier, entry in catalog_tools.items() if isinstance(entry, dict)}
    represented_tool_paths = {str(entry.get("path")) for entry in tool_entries.values()}
    for path in sorted((ROOT / "tools").glob("*.py")):
        if path.name.startswith("_"):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in represented_tool_paths:
            continue
        identifier = path.stem.replace("_", "-")
        if identifier in tool_entries:
            raise PresentationSyncError(f"duplicate tool ID: {identifier}")
        tool_entries[identifier] = {"version": 1, "path": relative}

    groups = (("agents", "agent", agent_entries), ("tools", "tool", tool_entries), ("templates", "template", catalog.get("templates", {})))
    for kind_plural, kind, entries in groups:
        entries = catalog.get(kind_plural, {})
        if kind == "agent":
            entries = agent_entries
        elif kind == "tool":
            entries = tool_entries
        if not isinstance(entries, dict):
            raise PresentationSyncError(f"catalog {kind_plural} must be an object")
        for identifier, entry in sorted(entries.items()):
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                raise PresentationSyncError(f"invalid {kind} catalog entry: {identifier}")
            path = ROOT / entry["path"]
            if path.is_dir():
                members = [item.relative_to(path).as_posix() for item in sorted(path.rglob("*")) if item.is_file()]
                text = "Directory template set:\n" + "\n".join(f"- {member}" for member in members)
            else:
                text = path.read_text(encoding="utf-8")
            if kind == "agent":
                data = read_json(path)
                description = str(data.get("description", ""))
                purpose, use_when, not_when = description_parts(description)
                nodes.append(
                    base_node(
                        identifier=identifier,
                        kind=kind,
                        path=path,
                        name=humanize(identifier),
                        description=description,
                        purpose=str(data.get("responsibility", purpose)),
                        use_when=use_when,
                        not_when=list_of_strings(data.get("forbidden_behavior")) or not_when,
                        inputs=list_of_strings(data.get("expected_inputs")),
                        workflow=list_of_strings(data.get("allowed_behavior")),
                        outputs=list_of_strings(data.get("expected_outputs")),
                        validation=[str(data.get("read_write_posture", ""))] if data.get("read_write_posture") else [],
                        tags=list_of_strings(data.get("capabilities_needed")),
                        search_terms=[identifier, humanize(identifier)] + list_of_strings(data.get("capabilities_needed")),
                        runtime_support=adapter_names,
                        source_text=json.dumps(data, indent=2, ensure_ascii=False),
                    )
                )
            else:
                description = text_summary(path, text)
                nodes.append(
                    base_node(
                        identifier=identifier,
                        kind=kind,
                        path=path,
                        name=humanize(identifier),
                        description=description,
                        purpose=description,
                        tags=list_of_strings(entry.get("provides", [])) + list_of_strings(entry.get("keywords", [])),
                        search_terms=[identifier, humanize(identifier)]
                        + list_of_strings(entry.get("aliases", []))
                        + list_of_strings(entry.get("provides", []))
                        + list_of_strings(entry.get("keywords", [])),
                        source_text=text,
                    )
                )
                if kind == "tool":
                    parts = Path(entry["path"]).parts
                    if len(parts) > 3 and parts[0] == "skills" and parts[1] in skill_ids and parts[2] == "scripts":
                        add_edge(edges, edge_seen, f"skill:{parts[1]}", f"tool:{identifier}", "ships tool", entry["path"])

    archetype_paths = sorted((ROOT / "archetypes").glob("*/archetype.yaml"))
    overlay_paths = sorted((ROOT / "archetypes" / "overlays").glob("*/overlay.yaml"))
    archetype_ids: set[str] = set()
    for kind, paths in (("archetype", archetype_paths), ("overlay", overlay_paths)):
        for path in paths:
            data = read_json(path)
            identifier = str(data.get("id", path.parent.name))
            if kind == "archetype":
                archetype_ids.add(identifier)
            description = str(data.get("purpose") or "; ".join(list_of_strings(data.get("intent"))))
            initialization = data.get("initialization", {}) if isinstance(data.get("initialization"), dict) else {}
            nodes.append(
                base_node(
                    identifier=identifier,
                    kind=kind,
                    path=path,
                    name=str(data.get("title", humanize(identifier))),
                    description=description,
                    purpose=description,
                    use_when=list_of_strings(data.get("intent")) or list_of_strings(data.get("compatible_archetypes")),
                    not_when=list_of_strings(data.get("not_for")),
                    inputs=list_of_strings(initialization.get("ask_if_unresolved", [])),
                    workflow=[str(item.get("id")) for item in data.get("conditions", []) if isinstance(item, dict) and item.get("id")],
                    outputs=list_of_strings(data.get("typical_outputs")) or list_of_strings(data.get("outputs")),
                    validation=list_of_strings(data.get("invariants")),
                    tags=list_of_strings(data.get("compatible_archetypes")),
                    search_terms=[identifier, str(data.get("title", humanize(identifier)))]
                    + list_of_strings(data.get("aliases"))
                    + list_of_strings(data.get("compatible_archetypes")),
                    runtime_support=adapter_names,
                    source_text=json.dumps(data, indent=2, ensure_ascii=False),
                )
            )
            composition_refs = all_composition_refs(data)
            for target_kind, target_id in composition_refs:
                add_edge(edges, edge_seen, f"{kind}:{identifier}", f"{target_kind}:{target_id}", "uses", path.relative_to(ROOT).as_posix())
            if kind == "archetype":
                for overlay in data.get("recommended_overlays", []):
                    if isinstance(overlay, dict) and overlay.get("id"):
                        add_edge(edges, edge_seen, f"archetype:{identifier}", f"overlay:{overlay['id']}", "recommends", path.relative_to(ROOT).as_posix())
            else:
                compatible_archetypes = list_of_strings(data.get("compatible_archetypes"))
                for archetype in compatible_archetypes:
                    add_edge(edges, edge_seen, f"overlay:{identifier}", f"archetype:{archetype}", "applies to", path.relative_to(ROOT).as_posix())
                    for target_kind, target_id in composition_refs:
                        add_edge(
                            edges,
                            edge_seen,
                            f"{target_kind}:{target_id}",
                            f"archetype:{archetype}",
                            "available in",
                            path.relative_to(ROOT).as_posix(),
                        )

    for path, data in adapters_data:
        identifier = str(data.get("id", path.parent.name))
        concepts = data.get("concepts", {}) if isinstance(data.get("concepts"), dict) else {}
        limitations = list_of_strings(data.get("limitations"))
        display_name = str(data.get("display_name", humanize(identifier)))
        description = f"Maps canonical Agent Commons capabilities into {display_name} using verified native concepts and explicit limitations."
        installation = data.get("installation", {}) if isinstance(data.get("installation"), dict) else {}
        nodes.append(
            base_node(
                identifier=identifier,
                kind="adapter",
                path=path,
                name=display_name,
                description=description,
                purpose=str(data.get("precedence", description)),
                use_when=[f"Expose canonical capabilities in {display_name}."],
                not_when=limitations,
                workflow=[f"{key}: {value}" for key, value in concepts.items()],
                outputs=[f"{key}: {value}" for key, value in installation.items()],
                validation=[f"Verified on {data.get('verified_on')}" if data.get("verified_on") else ""],
                tags=[str(value) for value in concepts.values()],
                search_terms=[identifier, display_name] + [str(value) for value in concepts.values()],
                source_text=json.dumps(data, indent=2, ensure_ascii=False),
            )
        )
        for archetype in sorted(archetype_ids):
            if concepts.get("archetypes") == "commons":
                add_edge(edges, edge_seen, f"adapter:{identifier}", f"archetype:{archetype}", "exposes composition", path.relative_to(ROOT).as_posix())

    eval_specs = [
        (ROOT / "evals" / "skills" / "scenarios.yaml", "skills", "skill-evaluations", "Skill evaluations"),
        (ROOT / "evals" / "agents" / "scenarios.yaml", "agents", "agent-evaluations", "Agent evaluations"),
        (ROOT / "evals" / "archetypes" / "scenarios.yaml", "archetypes", "archetype-evaluations", "Archetype evaluations"),
        (ROOT / "evals" / "external" / "scenarios.yaml", "scenarios", "external-evaluations", "External capability evaluations"),
        (ROOT / "evals" / "initialization" / "scenarios.yaml", "scenarios", "initializer-evaluations", "Initializer evaluations"),
        (ROOT / "evals" / "initialization" / "natural-language-scenarios.yaml", "scenarios", "natural-language-initializer-evaluations", "Natural-language initializer evaluations"),
    ]
    for path, root_key, identifier, name in eval_specs:
        text = path.read_text(encoding="utf-8")
        scenario_ids = eval_identifiers(path, root_key)
        nodes.append(
            base_node(
                identifier=identifier,
                kind="eval",
                path=path,
                name=name,
                description=f"Canonical evaluation scenarios for {name.lower()}.",
                purpose=f"Validate expected behavior, invariants, and failure cases for {name.lower()}.",
                workflow=scenario_ids,
                outputs=["positive, negative, ambiguous, invariant, and failure evidence where declared"],
                tags=scenario_ids,
                search_terms=[identifier, name] + scenario_ids,
                source_text=text,
            )
        )
        target_kind = {"skills": "skill", "agents": "agent", "archetypes": "archetype"}.get(root_key)
        if target_kind:
            for target_id in scenario_ids:
                add_edge(edges, edge_seen, f"eval:{identifier}", f"{target_kind}:{target_id}", "validates", path.relative_to(ROOT).as_posix())
        if identifier in {"initializer-evaluations", "natural-language-initializer-evaluations"}:
            add_edge(edges, edge_seen, f"eval:{identifier}", "skill:initialize-project", "validates", path.relative_to(ROOT).as_posix())
        if identifier == "external-evaluations":
            for target in ("search-external-capabilities", "review-external-capability"):
                add_edge(edges, edge_seen, f"eval:{identifier}", f"skill:{target}", "validates", path.relative_to(ROOT).as_posix())

    external_registry = read_json(ROOT / "external" / "sources.yaml")
    external_sources = external_registry.get("sources", [])
    if not isinstance(external_sources, list):
        raise PresentationSyncError("external sources must be a list")
    for entry in external_sources:
        if not isinstance(entry, dict) or not entry.get("id"):
            continue
        identifier = str(entry["id"])
        nodes.append(
            base_node(
                identifier=identifier,
                kind="external",
                path=ROOT / "external" / "sources.yaml",
                name=humanize(identifier),
                description=str(entry.get("description", "External capability source.")),
                purpose=str(entry.get("notes", entry.get("description", ""))),
                use_when=[f"Trust: {entry.get('trust', 'UNSPECIFIED')}", f"Tier: {entry.get('tier', 'n/a')}", f"Enabled: {entry.get('enabled', False)}"],
                tags=list_of_strings(entry.get("capability_categories")) + [str(entry.get("trust", ""))],
                search_terms=[identifier, humanize(identifier)] + list_of_strings(entry.get("capability_categories")),
                validation=[f"Last reviewed {entry.get('last_reviewed')}" if entry.get("last_reviewed") else ""],
                source_text=json.dumps(entry, indent=2, ensure_ascii=False),
            )
        )
        add_edge(edges, edge_seen, f"external:{identifier}", "skill:search-external-capabilities", "feeds discovery", "external/sources.yaml")

    external_index = read_json(ROOT / "external" / "index" / "capabilities.json")
    candidates = external_index.get("candidates", [])
    if isinstance(candidates, list):
        for entry in candidates:
            if not isinstance(entry, dict) or not entry.get("id"):
                continue
            identifier = str(entry["id"])
            path = ROOT / str(entry.get("review_path", "external/index/capabilities.json"))
            nodes.append(
                base_node(
                    identifier=identifier,
                    kind="external",
                    path=path,
                    name=str(entry.get("name", humanize(identifier))),
                    description=str(entry.get("purpose", "Reviewed external capability candidate.")),
                    purpose=str(entry.get("why_useful", entry.get("purpose", ""))),
                    use_when=list_of_strings(entry.get("relevance")),
                    not_when=["Discovery does not install or promote this capability automatically."],
                    workflow=list_of_strings(entry.get("commons_overlap")),
                    outputs=[str(entry.get("review_recommendation", ""))] if entry.get("review_recommendation") else [],
                    validation=[f"Review status: {entry.get('review_status', 'unknown')}", f"Security class: {entry.get('security_class', 'unknown')}"],
                    tags=[str(entry.get("source_trust", "")), str(entry.get("status", "")), str(entry.get("detected_runtime", ""))],
                    search_terms=[identifier, str(entry.get("name", humanize(identifier)))] + list_of_strings(entry.get("relevance")),
                    source_text=json.dumps(entry, indent=2, ensure_ascii=False),
                )
            )
            add_edge(edges, edge_seen, f"external:{identifier}", "skill:review-external-capability", "reviewed by", str(entry.get("review_path", "external/index/capabilities.json")))
            if "PROMOTION" in str(entry.get("status", "")):
                add_edge(edges, edge_seen, f"external:{identifier}", "skill:promote-to-commons", "feeds promotion", "external/index/capabilities.json")

    node_keys = {str(node["key"]) for node in nodes}
    if len(node_keys) != len(nodes):
        raise PresentationSyncError("duplicate capability IDs detected")
    invalid_types = sorted({str(node["type"]) for node in nodes} - VALID_TYPES)
    if invalid_types:
        raise PresentationSyncError(f"invalid capability types: {invalid_types}")
    invalid_edges = [edge for edge in edges if edge["source"] not in node_keys or edge["target"] not in node_keys]
    if invalid_edges:
        first = invalid_edges[0]
        raise PresentationSyncError(f"relationship references missing node: {first['source']} -> {first['target']}")

    related: dict[str, set[str]] = {key: set() for key in node_keys}
    archetypes_by_capability: dict[str, set[str]] = {key: set() for key in node_keys}
    for edge in edges:
        related[edge["source"]].add(edge["target"])
        related[edge["target"]].add(edge["source"])
        if edge["source"].startswith("archetype:"):
            archetypes_by_capability[edge["target"]].add(edge["source"].split(":", 1)[1])
        if edge["target"].startswith("archetype:"):
            archetypes_by_capability[edge["source"]].add(edge["target"].split(":", 1)[1])
    for node in nodes:
        key = str(node["key"])
        node["related_capabilities"] = sorted(related[key])
        node["archetypes"] = sorted(archetypes_by_capability[key])

    stats: dict[str, int] = {}
    for node in nodes:
        kind = str(node["type"])
        stats[f"{kind}s" if kind != "external" else "external"] = stats.get(f"{kind}s" if kind != "external" else "external", 0) + 1
    stats["relationships"] = len(edges)
    stats["external_sources"] = len(external_sources)
    stats["external_candidates"] = len(candidates) if isinstance(candidates, list) else 0
    stats["test_files"] = len(list((ROOT / "evals").rglob("test_*.py")))

    type_order = {kind: index for index, kind in enumerate(("skill", "agent", "tool", "archetype", "overlay", "adapter", "eval", "template", "external"))}
    nodes.sort(key=lambda item: (type_order.get(str(item["type"]), 99), str(item["name"]).lower(), str(item["key"])))
    edges.sort(key=lambda item: (item["source"], item["target"], item["relationship"]))
    return {
        "schema_version": 2,
        "library_version": VERSION_PATH.read_text(encoding="utf-8").strip(),
        "stats": stats,
        "nodes": nodes,
        "edges": edges,
    }


def rendered_asset() -> str:
    payload = json.dumps(build_payload(), indent=2, ensure_ascii=False, sort_keys=False).replace("<", "\\u003c")
    return f"{GENERATED_HEADER}{payload}{GENERATED_SUFFIX}"


def rendered_block() -> str:
    """Return the deterministic generated representation for legacy callers."""
    return rendered_asset()


def rendered_standalone(html: str, asset: str) -> str:
    """Inline generated data into the authored shell for single-file delivery."""
    matches = list(DATA_SCRIPT_RE.finditer(html))
    if len(matches) != 1:
        raise PresentationSyncError("presentation must load assets/library-data.js exactly once")
    indent = matches[0].group("indent")
    embedded = f"{indent}<script>\n{asset.rstrip()}\n{indent}</script>"
    return DATA_SCRIPT_RE.sub(lambda _match: embedded, html, count=1)


def replace_block(html: str, replacement: str) -> str:
    start = html.find(START)
    if start < 0:
        raise PresentationSyncError("presentation capability-data start marker is missing")
    end = html.find(END, start)
    if end < 0:
        raise PresentationSyncError("presentation capability-data end marker is missing")
    end += len(END)
    return f"{html[:start]}{replacement}{html[end:]}"


def parse_asset(text: str) -> dict[str, Any]:
    if not text.startswith(GENERATED_HEADER) or not text.endswith(GENERATED_SUFFIX):
        raise PresentationSyncError("generated presentation data header is invalid")
    raw = text[len(GENERATED_HEADER) : -len(GENERATED_SUFFIX)]
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PresentationSyncError(f"malformed generated presentation data: {exc}") from exc
    if not isinstance(payload, dict):
        raise PresentationSyncError("generated presentation payload must be an object")
    return payload


def payload_digest(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def payload_changes(previous: dict[str, Any] | None, current: dict[str, Any]) -> list[str]:
    if previous is None:
        return ["generated presentation data created"]
    changes: list[str] = []
    previous_nodes = {str(node["key"]): node for node in previous.get("nodes", []) if isinstance(node, dict) and node.get("key")}
    current_nodes = {str(node["key"]): node for node in current.get("nodes", []) if isinstance(node, dict) and node.get("key")}
    for key in sorted(current_nodes.keys() - previous_nodes.keys()):
        changes.append(f"+ {key}")
    for key in sorted(previous_nodes.keys() - current_nodes.keys()):
        changes.append(f"- {key}")
    for key in sorted(previous_nodes.keys() & current_nodes.keys()):
        if payload_digest(previous_nodes[key]) != payload_digest(current_nodes[key]):
            changes.append(f"~ {key}")
    old_edges = {
        (str(edge.get("source")), str(edge.get("target")), str(edge.get("relationship")))
        for edge in previous.get("edges", [])
        if isinstance(edge, dict)
    }
    new_edges = {
        (str(edge.get("source")), str(edge.get("target")), str(edge.get("relationship")))
        for edge in current.get("edges", [])
        if isinstance(edge, dict)
    }
    if old_edges != new_edges:
        changes.append(f"network relationships: {len(old_edges)} -> {len(new_edges)}")
    return changes


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    temporary.replace(path)


def sync() -> bool:
    expected = rendered_asset()
    parse_asset(expected)
    html = PRESENTATION_PATH.read_text(encoding="utf-8")
    expected_standalone = rendered_standalone(html, expected)
    current = DATA_PATH.read_text(encoding="utf-8") if DATA_PATH.exists() else ""
    current_standalone = STANDALONE_PATH.read_text(encoding="utf-8") if STANDALONE_PATH.exists() else ""
    changed = False
    if current != expected:
        write_atomic(DATA_PATH, expected)
        changed = True
    if current_standalone != expected_standalone:
        write_atomic(STANDALONE_PATH, expected_standalone)
        changed = True
    return changed


def validate() -> list[str]:
    try:
        current_html = PRESENTATION_PATH.read_text(encoding="utf-8")
        current_data = DATA_PATH.read_text(encoding="utf-8")
        current_standalone = STANDALONE_PATH.read_text(encoding="utf-8")
        expected_data = rendered_asset()
        expected_standalone = rendered_standalone(current_html, expected_data)
        payload = parse_asset(current_data)
    except (OSError, json.JSONDecodeError, PresentationSyncError) as exc:
        return [str(exc)]
    errors: list[str] = []
    if current_data != expected_data:
        errors.append("presentation factual data is stale; run tools/refresh_commons_presentation.py")
    if current_standalone != expected_standalone:
        errors.append("standalone presentation is stale; run tools/refresh_commons_presentation.py")
    if 'src="assets/library-data.js"' not in current_html:
        errors.append("presentation does not load assets/library-data.js")
    if 'id="capability-data"' in current_html:
        errors.append("presentation still embeds generated capability data in authored HTML")
    if DATA_SCRIPT_RE.search(current_standalone):
        errors.append("standalone presentation still loads assets/library-data.js")
    if re.search(r'<(?:script|img|source|video|audio)\b[^>]*\bsrc=["\'](?!data:)', current_standalone):
        errors.append("standalone presentation has a non-embedded source dependency")
    if re.search(r'<link\b[^>]*\bhref=["\'](?!data:)', current_standalone):
        errors.append("standalone presentation has a non-embedded linked dependency")
    if re.search(r"@import\s|url\(\s*(?!data:|[\"']data:)", current_standalone, re.IGNORECASE):
        errors.append("standalone presentation CSS has a non-embedded dependency")
    node_keys: set[str] = set()
    for node in payload.get("nodes", []):
        if not isinstance(node, dict):
            errors.append("generated presentation node is not an object")
            continue
        key = str(node.get("key", ""))
        if not key or key in node_keys:
            errors.append(f"duplicate or missing generated node key: {key}")
        node_keys.add(key)
        if node.get("type") not in VALID_TYPES:
            errors.append(f"invalid generated capability type: {node.get('type')}")
        source_path = node.get("path")
        if not isinstance(source_path, str) or Path(source_path).is_absolute() or ".." in Path(source_path).parts:
            errors.append(f"unsafe generated source path: {source_path}")
        elif not (ROOT / source_path).exists():
            errors.append(f"broken generated source path: {source_path}")
        preview = str(node.get("source_preview", ""))
        if re.search(r"/Users/|[A-Z]:\\\\Users\\\\", preview, re.IGNORECASE):
            errors.append(f"confidential local path in preview: {key}")
    edge_keys: set[tuple[str, str, str]] = set()
    for edge in payload.get("edges", []):
        if not isinstance(edge, dict):
            errors.append("generated presentation edge is not an object")
            continue
        marker = (str(edge.get("source")), str(edge.get("target")), str(edge.get("relationship")))
        if marker in edge_keys:
            errors.append(f"duplicate generated relationship: {marker}")
        edge_keys.add(marker)
        if marker[0] not in node_keys or marker[1] not in node_keys:
            errors.append(f"generated relationship references missing node: {marker[0]} -> {marker[1]}")
    serialized_payload = json.dumps(payload, ensure_ascii=False)
    if re.search(r"/Users/|[A-Z]:\\\\Users\\\\", serialized_payload, re.IGNORECASE):
        errors.append("generated presentation data contains a confidential local path")
    for required_id in [
        "network-search",
        "capability-graph",
        "network-reset",
        "capability-search",
        "capability-types",
        "capability-list",
        "capability-preview",
        "capability-source-preview",
        "diagram-capability-title",
    ]:
        if f'id="{required_id}"' not in current_html:
            errors.append(f"presentation interaction is missing {required_id}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", choices=("sync", "validate"), help=argparse.SUPPRESS)
    parser.add_argument("--check", action="store_true", help="detect stale generated data without writing")
    args = parser.parse_args(argv)
    if args.command == "validate" or args.check:
        errors = validate()
        if errors:
            print("Presentation data: STALE")
            for error in errors:
                print(f"ERROR {error}")
            return 1
        print("Presentation data: CURRENT")
        return 0
    if args.command in (None, "sync"):
        try:
            previous = parse_asset(DATA_PATH.read_text(encoding="utf-8")) if DATA_PATH.exists() else None
            current = build_payload()
            changed = sync()
        except (OSError, json.JSONDecodeError, PresentationSyncError) as exc:
            print(f"ERROR {exc}", file=sys.stderr)
            return 1
        if not changed:
            print("No presentation data changes.")
            return 0
        print("Presentation refreshed.")
        previous_stats = previous.get("stats", {}) if previous else {}
        current_stats = current.get("stats", {})
        for label in ("skills", "agents", "tools", "archetypes", "overlays", "adapters", "evals"):
            before = previous_stats.get(label, 0)
            after = current_stats.get(label, 0)
            print(f"{label.capitalize()}: {before} -> {after}")
        changes = payload_changes(previous, current)
        if changes:
            print("Changes detected:")
            for change in changes[:40]:
                print(change)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
