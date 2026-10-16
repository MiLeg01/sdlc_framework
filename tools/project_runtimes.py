#!/usr/bin/env python3
"""Inspect, verify, or remove thin runtime adapters and canonical project capability references."""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

from runtime_adapters import AdapterError, RUNTIMES, capability_path, render_claude_project_adapter


class ProjectRuntimeError(RuntimeError):
    """Project runtime state cannot be changed safely."""


def atomic_write(path: Path, content: str) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def runtime_block(text: str) -> tuple[list[str], int, int, list[str]]:
    lines = text.splitlines()
    try:
        start = lines.index("  runtimes:")
    except ValueError as exc:
        raise ProjectRuntimeError(".agent-commons.yaml has no project.runtimes block") from exc
    end = start + 1
    values: list[str] = []
    while end < len(lines) and lines[end].startswith("    - "):
        values.append(lines[end][6:].strip().strip('"'))
        end += 1
    if not values:
        raise ProjectRuntimeError("project.runtimes must contain at least one runtime")
    return lines, start, end, values


def manifest_list(text: str, section_name: str, key: str) -> list[str]:
    section = re.search(
        rf"(?m)^{re.escape(section_name)}:\s*$\n(?P<body>(?:^  .*\n?)*)",
        text,
    )
    if not section:
        raise ProjectRuntimeError(f".agent-commons.yaml has no {section_name} block")
    body = section.group("body")
    if re.search(rf"(?m)^  {re.escape(key)}:\s*\[\]\s*$", body):
        return []
    values = re.search(
        rf"(?m)^  {re.escape(key)}:\s*$\n(?P<body>(?:^    -\s+.*\n?)*)",
        body,
    )
    if not values:
        raise ProjectRuntimeError(f".agent-commons.yaml has no {section_name}.{key} list")
    return [
        value.strip().strip("'\"")
        for value in re.findall(r"(?m)^    -\s+(.*?)\s*$", values.group("body"))
    ]


def read_skill_references(text: str) -> list[str]:
    return manifest_list(text, "commons", "skills")


def manifest_path(root: Path) -> Path:
    path = root / ".agent-commons.yaml"
    if not path.is_file():
        raise ProjectRuntimeError(f"missing canonical project manifest: {path}")
    return path


def read_runtimes(root: Path) -> tuple[Path, str, list[str], tuple[list[str], int, int]]:
    path = manifest_path(root)
    text = path.read_text(encoding="utf-8")
    lines, start, end, values = runtime_block(text)
    invalid = sorted(set(values) - set(RUNTIMES))
    if invalid:
        raise ProjectRuntimeError(f"unknown project runtimes: {invalid}")
    return path, text, values, (lines, start, end)


def verify(root: Path) -> list[str]:
    issues: list[str] = []
    try:
        _, text, runtimes, _ = read_runtimes(root)
        skills = read_skill_references(text)
    except ProjectRuntimeError as exc:
        return [str(exc)]
    if not (root / "AGENTS.md").is_file():
        issues.append("missing shared project context: AGENTS.md")
    if "claude-code" in runtimes:
        claude = root / "CLAUDE.md"
        if not claude.is_file():
            issues.append("Claude Code is selected but CLAUDE.md is missing")
        elif claude.read_text(encoding="utf-8") != render_claude_project_adapter():
            issues.append("Claude Code adapter has drifted: CLAUDE.md")
    duplicate_skills = sorted({identifier for identifier in skills if skills.count(identifier) > 1})
    if duplicate_skills:
        issues.append(f"duplicate canonical skill references: {duplicate_skills}")
    for identifier in skills:
        try:
            capability_path("skills", identifier)
        except AdapterError:
            issues.append(f"unknown canonical skill reference: {identifier}")
    return issues


def remove_runtime(root: Path, runtime: str) -> None:
    path, text, runtimes, block = read_runtimes(root)
    if runtime not in runtimes:
        raise ProjectRuntimeError(f"runtime is not selected: {runtime}")
    remaining = [value for value in runtimes if value != runtime]
    if not remaining:
        raise ProjectRuntimeError("refusing to remove the last project runtime")
    adapter_path: Path | None = None
    if runtime == "claude-code":
        adapter_path = root / "CLAUDE.md"
        if adapter_path.exists() and adapter_path.read_text(encoding="utf-8") != render_claude_project_adapter():
            raise ProjectRuntimeError(f"refusing to remove changed Claude Code adapter: {adapter_path}")
    lines, start, end = block
    replacement = ["  runtimes:", *[f"    - {value}" for value in remaining]]
    updated = "\n".join(lines[:start] + replacement + lines[end:]) + ("\n" if text.endswith("\n") else "")
    atomic_write(path, updated)
    if adapter_path and adapter_path.exists():
        adapter_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("status", "verify", "remove"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--runtime", choices=RUNTIMES)
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    try:
        if args.command == "remove":
            if not args.runtime:
                parser.error("remove requires --runtime")
            remove_runtime(root, args.runtime)
            print(f"removed_runtime={args.runtime}")
            return 0
        _, text, runtimes, _ = read_runtimes(root)
        skills = read_skill_references(text)
        issues = verify(root)
        print(f"runtimes={','.join(runtimes)}")
        print("project_instructions=AGENTS.md")
        print("project_manifest=.agent-commons.yaml")
        print("capability_reference_mode=canonical-stable-id")
        print(f"selected_skills={','.join(skills)}")
        print("automatic_execution=false")
        if issues:
            print(f"status=issues count={len(issues)}")
            for issue in issues:
                print(f"ISSUE {issue}")
            return 1 if args.command == "verify" else 0
        print("status=ok")
        return 0
    except ProjectRuntimeError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
