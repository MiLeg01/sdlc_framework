#!/usr/bin/env python3
"""Discover and validate canonical Agent Commons skills from the filesystem."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
WORKSTATION_PATH_RE = re.compile(r"(?:/Users/|[A-Za-z]:[\\/]+Users[\\/])")


class SkillCatalogError(ValueError):
    """A canonical skill cannot be safely exposed to an agent runtime."""


@dataclass(frozen=True)
class CanonicalSkill:
    canonical_id: str
    directory: Path
    skill_file: Path
    name: str
    description: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class SkillInspection:
    canonical_id: str
    directory: Path
    skill_file: Path
    skill: CanonicalSkill | None
    errors: tuple[str, ...]


def _scalar(value: str, path: Path, key: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value[0] in {"'", '"'}:
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError) as exc:
            raise SkillCatalogError(f"{path}: invalid quoted YAML scalar for {key}: {exc}") from exc
        if not isinstance(parsed, str):
            raise SkillCatalogError(f"{path}: {key} must be a string")
        return parsed
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "~"}:
        return None
    return value


def parse_frontmatter(path: Path) -> dict[str, Any]:
    """Parse the top-level scalar YAML subset used by canonical SKILL.md files."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SkillCatalogError(f"{path}: missing YAML front matter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise SkillCatalogError(f"{path}: unterminated YAML front matter")
    metadata: dict[str, Any] = {}
    for line_number, line in enumerate(text[4:end].splitlines(), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1].isspace() or ":" not in line:
            raise SkillCatalogError(f"{path}:{line_number}: malformed top-level YAML entry")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        if not key or key in metadata:
            raise SkillCatalogError(f"{path}:{line_number}: duplicate or empty YAML key {key!r}")
        metadata[key] = _scalar(raw_value, path, key)
    return metadata


def validate_skill(directory: Path, *, check_workstation_paths: bool = True) -> CanonicalSkill:
    skill_file = directory / "SKILL.md"
    if not skill_file.is_file():
        raise SkillCatalogError(f"{directory}: SKILL.md is missing")
    metadata = parse_frontmatter(skill_file)
    name = metadata.get("name")
    description = metadata.get("description")
    if not isinstance(name, str) or not name.strip():
        raise SkillCatalogError(f"{skill_file}: name is missing or empty")
    if not SKILL_NAME_RE.fullmatch(name):
        raise SkillCatalogError(f"{skill_file}: name is not suitable for explicit ${name} invocation")
    if not isinstance(description, str) or not description.strip():
        raise SkillCatalogError(f"{skill_file}: description is missing or empty")
    if name != directory.name:
        raise SkillCatalogError(f"{skill_file}: name {name!r} does not match canonical ID {directory.name!r}")
    if check_workstation_paths and WORKSTATION_PATH_RE.search(skill_file.read_text(encoding="utf-8")):
        raise SkillCatalogError(f"{skill_file}: contains a workstation-specific absolute path")
    return CanonicalSkill(
        canonical_id=directory.name,
        directory=directory,
        skill_file=skill_file,
        name=name,
        description=description.strip(),
        metadata=metadata,
    )


def discover_canonical_skills(
    library: Path,
    *,
    check_workstation_paths: bool = True,
) -> list[CanonicalSkill]:
    """Return every valid canonical skill in stable filesystem order."""
    inspections = inspect_canonical_skills(library, check_workstation_paths=check_workstation_paths)
    errors = [error for inspection in inspections for error in inspection.errors]
    names: dict[str, Path] = {}
    skills: list[CanonicalSkill] = []
    for inspection in inspections:
        if inspection.skill is None:
            continue
        skill = inspection.skill
        if skill.name in names:
            errors.append(
                f"duplicate canonical skill name {skill.name!r}: {names[skill.name]} and {skill.skill_file}"
            )
            continue
        names[skill.name] = skill.skill_file
        skills.append(skill)
    if errors:
        raise SkillCatalogError("canonical skill validation failed:\n  - " + "\n  - ".join(errors))
    return skills


def inspect_canonical_skills(
    library: Path,
    *,
    check_workstation_paths: bool = True,
) -> list[SkillInspection]:
    """Return a complete canonical directory matrix, retaining invalid entries."""
    root = library / "skills"
    if not root.is_dir():
        raise SkillCatalogError(f"canonical skills directory is missing: {root}")
    inspections: list[SkillInspection] = []
    for directory in sorted((path for path in root.iterdir() if path.is_dir()), key=lambda path: path.name):
        try:
            skill = validate_skill(directory, check_workstation_paths=check_workstation_paths)
        except (OSError, SkillCatalogError) as exc:
            inspections.append(
                SkillInspection(
                    canonical_id=directory.name,
                    directory=directory,
                    skill_file=directory / "SKILL.md",
                    skill=None,
                    errors=(str(exc),),
                )
            )
            continue
        inspections.append(
            SkillInspection(
                canonical_id=directory.name,
                directory=directory,
                skill_file=skill.skill_file,
                skill=skill,
                errors=(),
            )
        )
    return inspections


def canonical_skill_map(library: Path) -> dict[str, CanonicalSkill]:
    return {skill.canonical_id: skill for skill in discover_canonical_skills(library)}
