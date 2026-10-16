#!/usr/bin/env python3
"""Render and validate thin runtime adapters from canonical Agent Commons capabilities."""

from __future__ import annotations

import argparse
import json
import sys
from functools import lru_cache
from pathlib import Path, PurePath
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "install"))
from skill_catalog import SkillCatalogError, canonical_skill_map, validate_skill


CATALOG_PATH = ROOT / "catalog" / "capabilities.yaml"
CODEX_INTERFACES_PATH = ROOT / "adapters" / "codex" / "skill-interfaces.yaml"
RUNTIMES = ("codex", "claude-code", "cline", "opencode")


class AdapterError(ValueError):
    """The canonical capability or runtime mapping is invalid."""


def load_json_yaml(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AdapterError(f"invalid JSON-compatible YAML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AdapterError(f"expected object in {path}")
    return value


@lru_cache(maxsize=None)
def load_catalog(library: Path = ROOT) -> dict[str, Any]:
    return load_json_yaml(library / "catalog" / "capabilities.yaml")


@lru_cache(maxsize=None)
def adapter_manifest(runtime: str) -> dict[str, Any]:
    if runtime not in RUNTIMES:
        raise AdapterError(f"unsupported runtime: {runtime}")
    return load_json_yaml(ROOT / "adapters" / runtime / "adapter.yaml")


@lru_cache(maxsize=None)
def runtime_user_path_parts(runtime: str, destination: str) -> tuple[str, ...]:
    """Return a runtime user destination as platform-neutral path components."""
    manifest = adapter_manifest(runtime)
    paths = manifest.get("user_paths")
    if not isinstance(paths, dict):
        raise AdapterError(f"adapter lacks user_paths: {runtime}")
    value = paths.get(destination)
    if not isinstance(value, list) or not value or not all(isinstance(part, str) and part for part in value):
        raise AdapterError(f"adapter lacks user path {destination!r}: {runtime}")
    return tuple(value)


def runtime_user_path(home: PurePath, runtime: str, destination: str) -> PurePath:
    return home.joinpath(*runtime_user_path_parts(runtime, destination))


def capability_entry(kind: str, identifier: str, library: Path = ROOT) -> dict[str, Any]:
    catalog = load_catalog(library)
    group = catalog.get(kind)
    if not isinstance(group, dict) or identifier not in group:
        raise AdapterError(f"unknown canonical {kind[:-1]}: {identifier}")
    return group[identifier]


def capability_path(kind: str, identifier: str, library: Path = ROOT) -> Path:
    if kind == "skills":
        skill = canonical_skill_map(library).get(identifier)
        if skill is None:
            raise AdapterError(f"unknown canonical skill: {identifier}")
        return skill.skill_file
    return library / capability_entry(kind, identifier, library)["path"]


def skill_metadata(identifier: str, library: Path = ROOT) -> dict[str, str]:
    try:
        skill = validate_skill(library / "skills" / identifier)
    except SkillCatalogError as exc:
        raise AdapterError(str(exc)) from exc
    return {"name": skill.name, "description": skill.description}


def agent_definition(identifier: str, library: Path = ROOT) -> dict[str, Any]:
    value = load_json_yaml(capability_path("agents", identifier, library))
    if value.get("id") != identifier or value.get("kind") != "agent":
        raise AdapterError(f"agent metadata mismatch: {identifier}")
    return value


def canonical_global_instructions(library: Path = ROOT) -> str:
    return (library / "adapters" / "global-instructions.md").read_text(encoding="utf-8").strip()


def wrapper_skill_name(runtime: str, identifier: str, kind: str = "skill") -> str:
    if kind == "agent" and runtime == "cline":
        return f"agent-{identifier}"
    return identifier


def render_skill_wrapper(runtime: str, identifier: str, library: Path = ROOT) -> str:
    if runtime not in {"cline", "opencode"}:
        raise AdapterError(f"{runtime} uses native symlinked skills instead of wrappers")
    metadata = skill_metadata(identifier, library)
    source = capability_path("skills", identifier, library)
    return f'''---
name: {identifier}
description: {metadata["description"]}
---

# Managed Agent Commons adapter

This file is generated for {adapter_manifest(runtime)["display_name"]}. Edit the canonical workflow instead.

Before acting, read `{source}` completely with the runtime's file-reading tool and follow that canonical workflow, including its trigger, non-trigger, validation, and failure rules. Resolve relative resources from `{source.parent}`.
'''


def render_agent(runtime: str, identifier: str, library: Path = ROOT) -> tuple[str, str]:
    agent = agent_definition(identifier, library)
    description = agent["description"]
    instructions = agent["instructions"]
    if runtime == "codex":
        body = (
            f'name = {json.dumps(identifier)}\n'
            f'description = {json.dumps(description)}\n\n'
            'developer_instructions = """\n'
            f'{instructions}\n'
            '"""\n'
        )
        return f"{identifier}.toml", body
    if runtime == "claude-code":
        body = f'''---
name: {identifier}
description: {description}
---

{instructions}
'''
        return f"{identifier}.md", body
    if runtime == "opencode":
        body = f'''---
description: {description}
mode: subagent
permission:
  edit: ask
  bash: ask
---

{instructions}
'''
        return f"{identifier}.md", body
    if runtime == "cline":
        name = wrapper_skill_name(runtime, identifier, "agent")
        source = capability_path("agents", identifier, library)
        body = f'''---
name: {name}
description: Apply the canonical {identifier} role when its independent responsibility materially improves the task.
---

# Managed Agent Commons role adapter

Cline does not document reusable custom subagent definitions with parity to this canonical role. Before acting, read `{source}`, adopt its responsibility and boundaries, and execute the work in the main agent or an available isolated read-only reviewer without claiming native custom-agent parity.
'''
        return "SKILL.md", body
    raise AdapterError(f"unsupported runtime: {runtime}")


def render_claude_project_adapter() -> str:
    return "@AGENTS.md\n\n## Claude Code adapter\n\nUse the shared project context above. Runtime-specific settings belong under `.claude/`; do not duplicate the project objective here.\n"


def validate_adapters(library: Path = ROOT, *, strict_catalog: bool = True) -> list[str]:
    errors: list[str] = []
    try:
        catalog = load_catalog(library)
    except AdapterError as exc:
        return [str(exc)]
    if catalog.get("schema_version") != 1:
        errors.append("capability catalog schema_version must be 1")
    kinds = catalog.get("capability_kinds")
    if kinds != ["skills", "agents", "tools", "templates"]:
        errors.append("capability catalog kinds must be skills/agents/tools/templates")
        kinds = ["skills", "agents", "tools", "templates"]
    filesystem_skill_ids = set(canonical_skill_map(library))
    catalog_skill_ids = set(catalog.get("skills", {}))
    if strict_catalog and filesystem_skill_ids != catalog_skill_ids:
        errors.append(
            "runtime-neutral skill catalog does not match canonical filesystem: "
            f"missing={sorted(filesystem_skill_ids - catalog_skill_ids)} "
            f"extra={sorted(catalog_skill_ids - filesystem_skill_ids)}"
        )
    seen_paths: set[str] = set()
    for kind in kinds:
        group = catalog.get(kind)
        if not isinstance(group, dict) or not group:
            errors.append(f"capability catalog {kind} must be non-empty")
            continue
        for identifier, entry in group.items():
            if not isinstance(entry, dict) or entry.get("version") != 1 or not isinstance(entry.get("path"), str):
                errors.append(f"invalid catalog entry: {kind}/{identifier}")
                continue
            if entry["path"] in seen_paths:
                errors.append(f"duplicate canonical path: {entry['path']}")
            seen_paths.add(entry["path"])
            if not (library / entry["path"]).exists():
                errors.append(f"missing canonical path: {entry['path']}")
    for identifier in filesystem_skill_ids:
        try:
            skill_metadata(identifier, library)
        except (AdapterError, OSError) as exc:
            errors.append(str(exc))
    try:
        interfaces = load_json_yaml(library / "adapters" / "codex" / "skill-interfaces.yaml")
        interface_map = interfaces.get("interfaces", {})
        if interfaces.get("schema_version") != 1 or not isinstance(interface_map, dict):
            errors.append("invalid Codex skill interface registry")
        else:
            skill_ids = filesystem_skill_ids
            interface_ids = set(interface_map)
            if interface_ids - skill_ids:
                errors.append(
                    "Codex skill interfaces contain unknown skills: "
                    f"extra={sorted(interface_ids - skill_ids)}"
                )
            for identifier, interface in interface_map.items():
                required = {"display_name", "short_description", "default_prompt"}
                if not isinstance(interface, dict) or not required <= set(interface):
                    errors.append(f"invalid Codex skill interface: {identifier}")
    except AdapterError as exc:
        errors.append(str(exc))
    for identifier in catalog.get("agents", {}):
        try:
            agent_definition(identifier)
        except AdapterError as exc:
            errors.append(str(exc))
    for runtime in RUNTIMES:
        try:
            manifest = adapter_manifest(runtime)
        except AdapterError as exc:
            errors.append(str(exc))
            continue
        if manifest.get("schema_version") != 1 or manifest.get("id") != runtime:
            errors.append(f"invalid adapter manifest identity: {runtime}")
        if not manifest.get("documentation") or not manifest.get("concepts"):
            errors.append(f"adapter lacks research or concept mapping: {runtime}")
        for destination in ("global_instructions", "skills", "agents"):
            try:
                runtime_user_path_parts(runtime, destination)
            except AdapterError as exc:
                errors.append(str(exc))
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")
    render = subparsers.add_parser("render")
    render.add_argument("--runtime", choices=RUNTIMES, required=True)
    render.add_argument("--kind", choices=("skill", "agent"), required=True)
    render.add_argument("--id", required=True)
    render.add_argument("--library", type=Path, default=ROOT)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "validate":
        errors = validate_adapters()
        print(f"runtimes={len(RUNTIMES)} errors={len(errors)}")
        for error in errors:
            print(f"ERROR {error}")
        return 1 if errors else 0
    try:
        if args.kind == "skill":
            print(render_skill_wrapper(args.runtime, args.id, args.library), end="")
        else:
            _, content = render_agent(args.runtime, args.id, args.library)
            print(content, end="")
        return 0
    except (AdapterError, OSError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
