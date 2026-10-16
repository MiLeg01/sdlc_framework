#!/usr/bin/env python3
"""Generate the fast capability routing index from canonical Commons metadata."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "catalog" / "capability-index.json"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def skill_description(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"(?m)^description:\s*(.+)$", text)
    return match.group(1).strip() if match else ""


def split_routing(description: str) -> tuple[str, str, str]:
    do_not = description.find(" Do not use")
    positive = description[:do_not].strip() if do_not >= 0 else description
    non_trigger = description[do_not + 1:].strip() if do_not >= 0 else ""
    use_when = positive.find(" Use when")
    trigger = positive[use_when + 1:].strip() if use_when >= 0 else positive
    summary = positive[:use_when].strip() if use_when >= 0 else positive
    return summary, trigger, non_trigger


def composition_membership() -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    contract = read_json(ROOT / "archetypes" / "composition.yaml")
    archetypes: dict[str, set[str]] = {}
    overlays: dict[str, set[str]] = {}
    for registry, target in (("archetypes", archetypes), ("overlays", overlays)):
        for identifier, entry in contract[registry].items():
            manifest = read_json(ROOT / "archetypes" / entry["path"])
            for group in manifest.get("capabilities", {}).values():
                for skill in group.get("skills", []):
                    target.setdefault(skill, set()).add(identifier)
            for condition in manifest.get("conditions", []):
                for skill in condition.get("capabilities", {}).get("skills", []):
                    target.setdefault(skill, set()).add(identifier)
    return archetypes, overlays


def runtime_support(kind: str) -> list[str]:
    supported: list[str] = []
    concept = {"skills": "skills", "agents": "custom_agents", "tools": "mcp", "templates": "project_instructions"}.get(kind)
    for path in sorted((ROOT / "adapters").glob("*/adapter.yaml")):
        adapter = read_json(path)
        if concept and adapter.get("concepts", {}).get(concept) not in {None, "unsupported"}:
            supported.append(str(adapter["id"]))
    return supported


def generate() -> dict[str, Any]:
    catalog = read_json(ROOT / "catalog" / "capabilities.yaml")
    archetypes, overlays = composition_membership()
    entries: list[dict[str, Any]] = []
    for kind in catalog.get("capability_kinds", []):
        for identifier, metadata in sorted(catalog.get(kind, {}).items()):
            description = str(metadata.get("description", ""))
            if kind == "skills":
                description = description or skill_description(ROOT / metadata["path"])
            summary, trigger, non_trigger = split_routing(description)
            entries.append({
                "id": identifier,
                "type": kind[:-1],
                "description": summary,
                "trigger": trigger,
                "non_trigger": non_trigger,
                "archetypes": sorted(archetypes.get(identifier, set())),
                "overlays": sorted(overlays.get(identifier, set())),
                "dependencies": sorted(metadata.get("related", [])),
                "provides": sorted(metadata.get("provides", [])),
                "runtime_availability": runtime_support(kind),
                "path": metadata["path"],
            })
    return {"schema_version": 1, "generated_from": ["catalog/capabilities.yaml", "archetypes/composition.yaml", "adapters/*/adapter.yaml"], "capabilities": entries}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = json.dumps(generate(), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != expected:
            print(f"capability index drift: {args.output}")
            return 1
        print(f"capability index current: {args.output}")
        return 0
    args.output.write_text(expected, encoding="utf-8")
    print(f"generated {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
